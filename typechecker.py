from parser import parse

arithmetic_operators = ["+", "-", "*", "/", "^","%","//"]
comparison_operators = ["==", "!=", "<", ">", "<=", ">="]
logical_operators = ["and", "or", "not"]
bitwise_operators = ["&", "|", "~~"]

class TypeChecker:
    def __init__(self):
        self.scopes = [{}]  # Stack of symbol tables (each scope is a dict)
        self.functions = {}

    def enter_scope(self):
        self.scopes.append({})  

    def exit_scope(self):
        self.scopes.pop()  

    def declare_variable(self, name, var_type):
        # if name in self.scopes[-1]:  # Shadowing check
        #     raise NameError(f"Variable '{name}' is already declared in this scope.")
        self.scopes[-1][name] = var_type

    def lookup_variable(self, name):
        for scope in reversed(self.scopes):  # Start from innermost scope
            if name in scope:
                return scope[name]
        if name in self.scopes[0]:  # Check global scope
            return self.scopes[0]
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
                    return 'float' if left_type == 'float' or right_type == 'float' else 'int'
                
                if node.op in comparison_operators:
                    if (node.op == "==" or node.op =="!="):
                        if left_type != right_type:
                            raise TypeError(f'Invalid operand types {left_type}, {right_type} for {node.op}')
                        return 'bool'
                    elif left_type not in ('int', 'float') or right_type not in ('int', 'float'):
                        raise TypeError(f'Invalid operand types {left_type}, {right_type} for {node.op}')
                    return 'bool'
                
                if node.op in logical_operators:
                    #### not ??
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
                            raise TypeError(f"Bitwise operators only support int, but got {right_type}")
                    elif left_type != "int" or right_type != "int":
                        raise TypeError(f"Bitwise operators only support int, but got {left_type} {node.op} {right_type}")
                    return "int"  # Bitwise operations always return int
                
            case 'Function':
                self.functions[node.name] = (node.params, node.return_type)
                self.declare_variable(node.name, 'fn')

                self.enter_scope()  # Enter function scope
                for param_type, param_name in node.params:
                    self.declare_variable(param_name, param_type)
                return_type = self.visit(node.body)
                if return_type is None:
                    return_type = "void"
                if return_type != node.return_type and return_type != "undefined":
                    raise TypeError(f'Function {node.name} return type mismatch: expected {node.return_type}, got {return_type}')
                self.exit_scope()  # Exit function scope
                return "fn"
            
            case 'Return':
                return self.visit(node.value)
            
            case 'FunctionCall':
                if node.name in self.functions:
                    expected_params, return_type = self.functions[node.name]
                    if len(node.params) != len(expected_params):
                        raise TypeError(f'Function {node.name} expects {len(expected_params)} arguments, got {len(node.params)}')
                    
                    for (expected_type, _), arg in zip(expected_params, node.params):
                        arg_type = self.visit(arg)
                        if arg_type != expected_type:
                            raise TypeError(f'Function {node.name} argument type mismatch: expected {expected_type}, got {arg_type}')
                    return return_type

                # Else, check if it's a variable holding a function
                else:
                    try:
                        var_type = self.lookup_variable(node.name)
                        if var_type != 'fn':
                            raise TypeError(f"'{node.name}' is not callable (type {var_type})")
                        
                        for arg in node.params:
                            self.visit(arg)

                        return 'undefined'  # Or you could track the return type later
                    except NameError:
                        raise NameError(f'Function {node.name} not declared')
              
            case 'Sequence':
                last_type = None
                return_val = None
                for stmt in node.statements:
                    last_type=self.visit(stmt)
                    if type(stmt).__name__=='Return':
                        return_val = last_type
                    if return_val is not None:
                        return return_val
    
            case 'Cond':  
                # Ensure all conditions are boolean
                if node.If:
                    cond_type = self.visit(node.If[0])
                    if cond_type != 'bool':
                        raise TypeError("Condition must be of type 'bool'")
                    # self.enter_scope()
                    self.visit(node.If[1])  # Visit if-body
                    # self.exit_scope()
                
                for cond, body in node.Elif:
                    cond_type = self.visit(cond)
                    if cond_type != 'bool':
                        raise TypeError("Condition must be of type 'bool'")
                    # self.enter_scope()
                    self.visit(body)  # Visit elif-body
                    # self.exit_scope()
                
                if node.Else:
                    # self.enter_scope()
                    self.visit(node.Else)
                    # self.exit_scope()

            case 'While':
                cond_type = self.visit(node.condition)
                if cond_type != 'bool':
                    raise TypeError("Condition must be of type 'bool'")
                # self.enter_scope()
                self.visit(node.body)
                # self.exit_scope()

            case "For":
                # self.enter_scope()
                self.visit(node.init)
                cond_type = self.visit(node.condition)
                if cond_type != 'bool':
                    raise TypeError("Condition must be of type 'bool'")
                self.visit(node.increment)
                self.visit(node.body)
                # self.exit_scope()

            case "Print":
                for val in node.values:
                    self.visit(val)
            
            case "Array":
                if not node.elements:
                    return "undefined"

                first_type = self.visit(node.elements[0])

                for elem in node.elements:
                    elem_type = self.visit(elem)
                    if elem_type != first_type:
                        raise TypeError(f"Array elements must be of the same type, but found {first_type} and {elem_type}")

                return f"{first_type}[]"
            
            case "ArrayAccess":
                collection_type = self.visit(node.array)

                # Check for array
                if "[]" in collection_type:
                    element_type = collection_type.replace("[]", "")

                    index_type = self.visit(node.index)
                    if index_type != "int":
                        raise TypeError(f"Array index must be of type int, but got {index_type}")
                    
                    return element_type

                # Check for hashmap
                elif collection_type.startswith("hashmap<"):
                    key_type_expected, value_type = collection_type[8:-1].split(",")

                    index_type = self.visit(node.index)
                    if index_type.strip() != key_type_expected.strip():
                        raise TypeError(f"Hashmap key must be of type {key_type_expected}, but got {index_type}")

                    return value_type.strip()
                
                elif collection_type == "string":
                    index_type = self.visit(node.index)
                    if index_type != "int":
                        raise TypeError(f"String index must be of type int, but got {index_type}")

                    return "string"

                # Not indexable
                else:
                    raise TypeError(f"Cannot index non-array/hashmap type {collection_type}")

           
            case "ArrayAppend":
                container_type = self.visit(node.array)

                # Array append
                if "[]" in container_type:
                    element_type = container_type.replace("[]", "")
                    value_type = self.visit(node.value)

                    if value_type != element_type:
                        raise TypeError(f"Cannot append value of type {value_type} to array of {element_type}")

                    return container_type
            
            case "ArrayDelete":
                collection_type = self.visit(node.array)

                # Array delete: delete by index
                if "[]" in collection_type:
                    index_type = self.visit(node.index)
                    if index_type != "int":
                        raise TypeError(f"Array index must be of type int, but got {index_type}")
                    return collection_type

                # Map delete: delete by key
                elif collection_type.startswith("hashmap<"):
                    key_type_expected, value_type = collection_type[8:-1].split(",")
                    
                    key_type = self.visit(node.index)

                    if key_type != key_type_expected:
                        raise TypeError(f"Key type mismatch in map delete: expected {key_type_expected}, got {key_type}")
                    return collection_type

                else:
                    raise TypeError(f"Cannot delete from non-array/map type: {collection_type}")

            case "ArrayAssignment":
                collection_type = self.visit(node.array)

                # Array case
                if "[]" in collection_type:
                    element_type = collection_type.replace("[]", "")

                    index_type = self.visit(node.index)
                    if index_type != "int":
                        raise TypeError(f"Array index must be of type int, but got {index_type}")

                    value_type = self.visit(node.value)
                    if value_type != element_type:
                        raise TypeError(f"Type mismatch: array expects {element_type}, but got {value_type}")

                    return value_type

                # Hashmap case
                elif collection_type.startswith("hashmap<"):
                    key_type_expected, value_type_expected = collection_type[8:-1].split(",")

                    index_type = self.visit(node.index)
                    if index_type.strip() != key_type_expected.strip():
                        raise TypeError(f"Hashmap key must be of type {key_type_expected}, but got {index_type}")

                    value_type = self.visit(node.value)
                    if value_type.strip() != value_type_expected.strip():
                        raise TypeError(f"Type mismatch: hashmap expects {value_type_expected}, but got {value_type}")

                    return value_type
                
                elif collection_type == "string":
                    index_type = self.visit(node.index)
                    if index_type != "int":
                        raise TypeError(f"String index must be of type int, but got {index_type}")

                    value_type = self.visit(node.value)
                    if value_type != "string":
                        raise TypeError(f"Type mismatch: string expects string, but got {value_type}")

                    return value_type

                else:
                    raise TypeError(f"Cannot assign to non-array/hashmap type {collection_type}")

            
            case "ArrayLength":
                collection_type = self.visit(node.array)

                if "[]" in collection_type or collection_type == "string":
                    return "int"

                elif collection_type.startswith("hashmap<"):
                    return "int"

                else:
                    raise TypeError(f"Cannot get length of non-array/hashmap type {collection_type}")


            case "Parenthesis":
                return self.visit(node.expr)
            
            case "HashMap":
                index_type = node.index_type
                value_type = node.value_type

                if index_type not in ('int', 'string', 'float', 'bool'):
                    raise TypeError(f"Invalid key type {index_type} for hashmap; only int, string, float, bool are allowed")
                self.declare_variable(node.name, f"hashmap<{index_type}, {value_type}>")

                return f"hashmap<{index_type}, {value_type}>"
            
            case _:
                pass
