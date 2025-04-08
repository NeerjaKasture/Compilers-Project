from parser import parse

arithmetic_operators = ["+", "-", "*", "/", "^", "%", "//"]
comparison_operators = ["==", "!=", "<", ">", "<=", ">="]
logical_operators = ["and", "or", "not"]
bitwise_operators = ["&", "|", "~~"]

class TypeChecker:
    def __init__(self):
        self.scopes = [{}]  # Stack of symbol tables

    def enter_scope(self):
        self.scopes.append({})

    def exit_scope(self):
        self.scopes.pop()

    def declare_variable(self, name, var_type):
        self.scopes[-1][name] = var_type

    def lookup_variable(self, name):
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        raise NameError(f"Variable {name} not declared")

    def visit(self, node):
        method_name = type(node).__name__

        match method_name:
            case 'Number':
                return 'int' if '.' not in node.val else 'float'

            case 'Boolean':
                return 'bool'

            case 'Variable':
                return self.lookup_variable(node.val)

            case 'String':
                return 'string'

            case 'Input':
                return "undefined"

            case 'Declaration':
                value_type = self.visit(node.value)
                if value_type != node.type and value_type != "undefined":
                    raise TypeError(f'Type mismatch: expected {node.type}, got {value_type}')
                self.declare_variable(node.name, node.type)
                return node.type

            case 'Assignment':
                value_type = self.visit(node.value)
                var_type = self.lookup_variable(node.name)
                if value_type != var_type and value_type != "undefined":
                    raise TypeError(f'Type mismatch: expected {var_type}, got {value_type}')
                return value_type

            case 'BinOp':
                left_type = self.visit(node.left)
                right_type = self.visit(node.right)

                if node.op in arithmetic_operators:
                    if left_type not in ('int', 'float') or right_type not in ('int', 'float'):
                        raise TypeError(f'Invalid operand types {left_type}, {right_type} for {node.op}')
                    return 'float' if 'float' in (left_type, right_type) else 'int'

                if node.op in comparison_operators:
                    if node.op in ("==", "!="):
                        if left_type != right_type:
                            raise TypeError(f'Invalid operand types {left_type}, {right_type} for {node.op}')
                        return 'bool'
                    elif left_type not in ('int', 'float') or right_type not in ('int', 'float'):
                        raise TypeError(f'Invalid operand types {left_type}, {right_type} for {node.op}')
                    return 'bool'

                if node.op in logical_operators:
                    if node.op == "not":
                        if left_type != 'bool':
                            raise TypeError(f'Unsupported operand type {left_type} for {node.op}')
                    else:
                        if left_type != 'bool' or right_type != 'bool':
                            raise TypeError(f'Invalid operand types {left_type}, {right_type} for {node.op}')
                    return 'bool'

                if node.op in bitwise_operators:
                    if node.op == "~~":
                        if right_type != "int":
                            raise TypeError(f"Bitwise operator '~~' requires int, got {right_type}")
                    elif left_type != "int" or right_type != "int":
                        raise TypeError(f"Bitwise operators only support int, but got {left_type} {node.op} {right_type}")
                    return "int"

            case 'Function':
                # Store function signature as a tuple in symbol table
                self.declare_variable(node.name, ('fn', node.params, node.return_type))

                self.enter_scope()
                for param_type, param_name in node.params:
                    self.declare_variable(param_name, param_type)

                return_type = self.visit(node.body)
                if return_type is None:
                    return_type = "void"

                if return_type != node.return_type and return_type != "undefined":
                    raise TypeError(f'Function {node.name} return type mismatch: expected {node.return_type}, got {return_type}')
                self.exit_scope()

                return "fn"

            case 'Return':
                return self.visit(node.value)

            case 'FunctionCall':
                func_info = self.lookup_variable(node.name)

                if isinstance(func_info, tuple) and func_info[0] == 'fn':
                    expected_params, return_type = func_info[1], func_info[2]

                    if len(node.params) != len(expected_params):
                        raise TypeError(f'Function {node.name} expects {len(expected_params)} arguments, got {len(node.params)}')

                    for (expected_type, _), arg in zip(expected_params, node.params):
                        arg_type = self.visit(arg)
                        if arg_type != expected_type:
                            raise TypeError(f'Function {node.name} argument type mismatch: expected {expected_type}, got {arg_type}')

                    return return_type

                raise TypeError(f"'{node.name}' is not callable (type {func_info})")

            case 'Sequence':
                return_val = None
                for stmt in node.statements:
                    last_type = self.visit(stmt)
                    if type(stmt).__name__ == 'Return':
                        return_val = last_type
                        break
                return return_val

            case 'Cond':
                if node.If:
                    cond_type = self.visit(node.If[0])
                    if cond_type != 'bool':
                        raise TypeError("Condition must be of type 'bool'")
                    self.visit(node.If[1])

                for cond, body in node.Elif:
                    cond_type = self.visit(cond)
                    if cond_type != 'bool':
                        raise TypeError("Condition must be of type 'bool'")
                    self.visit(body)

                if node.Else:
                    self.visit(node.Else)

            case 'While':
                cond_type = self.visit(node.condition)
                if cond_type != 'bool':
                    raise TypeError("Condition must be of type 'bool'")
                self.visit(node.body)

            case 'For':
                self.visit(node.init)
                cond_type = self.visit(node.condition)
                if cond_type != 'bool':
                    raise TypeError("Condition must be of type 'bool'")
                self.visit(node.increment)
                self.visit(node.body)

            case 'Print':
                for val in node.values:
                    self.visit(val)

            case 'Array':
                if not node.elements:
                    return "undefined"
                first_type = self.visit(node.elements[0])
                for elem in node.elements:
                    elem_type = self.visit(elem)
                    if elem_type != first_type:
                        raise TypeError(f"Array elements must be of the same type, but found {first_type} and {elem_type}")
                return f"{first_type}[]"

            case 'ArrayAccess':
                array_type = self.visit(node.array)
                if "[]" not in array_type and array_type != "string":
                    raise TypeError(f"Cannot index non-array type {array_type}")
                index_type = self.visit(node.index)
                if index_type != "int":
                    raise TypeError(f"Array index must be of type int, got {index_type}")
                return array_type.replace("[]", "") if "[]" in array_type else "string"

            case 'ArrayAssignment':
                array_type = self.visit(node.array)
                if "[]" not in array_type and array_type != "string":
                    raise TypeError(f"Cannot assign to non-array type {array_type}")
                index_type = self.visit(node.index)
                if index_type != "int":
                    raise TypeError(f"Array index must be of type int, got {index_type}")
                element_type = array_type.replace("[]", "") if "[]" in array_type else "string"
                value_type = self.visit(node.value)
                if value_type != element_type:
                    raise TypeError(f"Type mismatch: expected {element_type}, got {value_type}")
                return value_type

            case 'ArrayLength':
                array_type = self.visit(node.array)
                if "[]" not in array_type and array_type != "string":
                    raise TypeError(f"Cannot get length of non-array type {array_type}")
                return "int"

            case 'Parenthesis':
                return self.visit(node.expr)

            case _:
                pass
