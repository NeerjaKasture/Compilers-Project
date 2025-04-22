from keywords import *
from lexer import *
from parser import *
from errors import *

def is_array_type(type_str: str) -> bool:
    return type_str.endswith('[]')

def get_base_type(type_str: str) -> str:
    return type_str[:-2] if is_array_type(type_str) else type_str

class Stack:
    def __init__(self):
        self.items = []
    
    def push(self, item):
        self.items.append(item)
    
    def pop(self):
        if not self.items:
            raise RuntimeError("Stack underflow")
        self.items.pop()
    
    def top(self):
        if not self.items:
            raise RuntimeError("Stack is empty")
        return self.items[-1]
    
class Queue:
    def __init__(self):
        self.items = []
    
    def push(self, item):
        self.items.append(item)
    
    def pop(self):
        if not self.items:
            raise RuntimeError("Queue underflow")
        return self.items.pop(0)  # Remove and return first element
    
    def first(self):
        if not self.items:
            raise RuntimeError("Queue is empty")
        return self.items[0]  # Return first element without removing it

MAX_RECURSION_DEPTH = 1000
def e(tree: AST, env={}, types={}, call_stack=[]):
    match tree:
        case Input():
            word = input()
            if word == "nocap":
                return True
            elif word == "cap":
                return False
            elif word.count('.') == 1 and word.replace('.', '').isdigit():
                    return float(word)
            elif word.isdigit():
                return int(word)
            else:
                return word           
            
        case Variable(v):
            if call_stack:    
                local_env, _ = call_stack[-1]
                if v in local_env:
                    return local_env[v]
            

            if v in env:  # Fallback to global scope
                return env[v]
            raise NameError(f"Undefined variable: {v}")


        case Function(name, params, return_type, body):  
            env[name] = tree  
            return None  

        case FunctionCall(name, args):
            if name not in env or not isinstance(env[name], Function):
                raise NameError(f"Undefined function: {name}")

            func = env[name]
            if not isinstance(func, Function):
                raise TypeError(f"'{name}' is not a function")
            if len(args) != len(func.params):
                raise TypeError(f"Function '{name}' expects {len(func.params)} arguments but got {len(args)}")
                    
            # This means that all var in env are global and accessible by function to read only
            local_env = env.copy()
            local_types = types.copy()

            # Bind function arguments
            for (param_type, param_name), arg in zip(func.params, args):
                arg_value = e(arg, local_env, local_types)
                
                if param_type == "fn":
                    if not isinstance(arg_value, Function):
                        raise TypeError(f"Argument '{param_name}' must be a function")
                else:
                    if not isinstance(arg_value, datatypes[param_type]):
                        raise TypeError(f"Argument '{param_name}' must be of type {param_type}")

                local_env[param_name] = arg_value
                local_types[param_name] = param_type 
            
            call_stack.append((local_env,local_types))   
            if(len(call_stack)>MAX_RECURSION_DEPTH):
                raise RecursionLimitError(name)
            result = e(func.body, local_env, local_types,call_stack)
            result=e(result)
            if func.return_type != "void":
                if func.return_type == "fn":
                    if not isinstance(result, Function):
                        raise TypeError(f"Function '{name}' must return a function, but got {type(result).__name__}")
                else:
                    if not isinstance(result, datatypes[func.return_type]):
                        raise TypeError(f"Function '{name}' must return a value of type {func.return_type}, but got {type(result).__name__}")
                
            call_stack.pop()

            return result
        
        case Return(expr):
            if not call_stack:
                raise RuntimeError("Return statement executed outside of function scope")
            local_env,local_types = call_stack[-1]
           
            res = e(expr, local_env, local_types,call_stack)
            
            return res

        case Boolean(v):
            if v == "nocap":
                return True 
            elif v == "cap":
                return False
        case Parenthesis(expr):
            return e(expr)
        case Number(v):
            if '.' in v:
                return float(v)
            else:
                return int(v)
        case BinOp(op, l, r):
            if isinstance(e(l), bool) or isinstance(e(r), bool):
                if op in {"%","+", "-", "*", "/", "^","<",">","<=",">=","&","|","~~","//"}:
                    raise TypeError(f"Cannot apply '{op}' to Boolean type")
                match op:
                    case "and":
                        return e(l) and e(r)
                    case "or":
                        return e(l) or e(r)
                    case "not":
                        return not e(r)
            if isinstance(e(l), str) or isinstance(e(r), str):
                if op in {"%","+", "-", "*", "/", "^","<",">","<=",">=","&","|","~~","//"}:
                    raise TypeError(f"Cannot apply '{op}' to String type")  
            match op:
                case "+":
                    return e(l) + e(r)
                case "-":
                    return e(l) - e(r)
                case "*":
                    return e(l) * e(r)
                case "/":
                    if e(r) == 0:
                        raise ZeroDivisionError("Division by zero")
                    return e(l) / e(r)
                case  "%":
                    if e(r) == 0:
                        raise ZeroDivisionError("Division by zero")
                    return e(l) % e(r)
                case "^":
                    return e(l) ** e(r)
                case "<":
                    return e(l) < e(r)
                case ">":
                    return e(l) > e(r)
                case "<=":
                    return e(l) <= e(r)
                case ">=":
                    return e(l) >= e(r)
                case "==":
                    return e(l) == e(r)
                case "!=":
                    return e(l) != e(r)
                case "&":  # Bitwise AND
                    return e(l) & e(r)
                case "|":  # Bitwise OR
                    return e(l) | e(r)
                case "~~":  # Bitwise NOT (unary)
                    return ~e(r)  # Only use `left`, `right` is None
                case "//":  # Floor division
                    if e(r) == 0:
                        raise ZeroDivisionError("Division by zero")
                    return e(l) // e(r)
        case Cond(If, Elif, Else):
            if e(If[0]):
                
                return e(If[1])  # Execute the 'If' body

            # If there are any 'elif' conditions, check each one
            if Elif:  # Check if Elif is not empty
                for elif_condition, elif_body in Elif:
                    if e(elif_condition):  # Evaluating 'elif' condition
                        return e(elif_body)  # Execute the corresponding 'elif' body

            # If no condition matched, check 'Else' (if exists)
            if Else is not None:
                return e(Else)  # Execute the 'Else' body

            # Default return value if no conditions matched
            return None
        
        case Declaration(var_type, var_name, value):
            local_env = env
            local_types = types
            if call_stack:
                local_env, local_types = call_stack[-1]

            val = e(value, local_env, local_types)
            if val is None:
                raise ValueError(f"Failed to get valid input for {var_name}")

            if is_array_type(var_type):
                if not isinstance(val, list):
                    raise TypeError(f"Variable '{var_name}' must be of type {var_type}")
                base_type_str = get_base_type(var_type)
                if base_type_str == "fn":
                    if not all(isinstance(x, Function) for x in val):
                        raise TypeError(f"All elements in array '{var_name}' must be functions")
                else:
                    base_type = datatypes[base_type_str]
                    if not all(isinstance(x, base_type) for x in val):
                        raise TypeError(f"All elements in array '{var_name}' must be of type {base_type_str}")

            elif var_type == "fn":
                if not isinstance(val, Function):
                    raise TypeError(f"Variable '{var_name}' must be a function")
            else:
                if not isinstance(val, datatypes[var_type]):
                    raise TypeError(f"Variable '{var_name}' must be of type {var_type}")

            local_env[var_name] = val
            local_types[var_name] = var_type  # Keep string type info
            return

        case Assignment(var_name, value):
            local_env = env
            local_types = types
            if call_stack:
                local_env, local_types = call_stack[-1]

            if var_name not in local_env:
                raise NameError(f"Undefined variable: {var_name}")

            val = e(value, local_env, local_types)
            var_type = local_types[var_name]

            if is_array_type(var_type):
                if not isinstance(val, list):
                    raise TypeError(f"Variable '{var_name}' must be of type {var_type}")
                base_type = datatypes[get_base_type(var_type)]
                if not all(isinstance(x, base_type) for x in val):
                    raise TypeError(f"All elements in array '{var_name}' must be of type {get_base_type(var_type)}")
            elif var_type == "fn":
                if not isinstance(val, Function):
                    raise TypeError(f"Variable '{var_name}' must be a function")
            else:
                if not isinstance(val, datatypes[var_type]):
                    raise TypeError(f"Variable '{var_name}' must be of type {var_type}")

            local_env[var_name] = val
            return

        
        case While(condition, body):
            while e(condition, env, types):
                if isinstance(body, Sequence):
                    for stmt in body.statements:
                        result = e(stmt, env, types)
                        if result == "break":
                            return None 
                        elif result == "continue":
                            break 
                        elif isinstance(result,Return):
                            return result
                        elif isinstance(stmt, Return):
                            # If return is encountered, stop execution
                            return stmt 
                else:
                    result = e(body, env, types)
                    if result == "break":
                        return None  
                    if result == "continue":
                        continue 
                    if isinstance(result,Return):
                        return result
                    elif isinstance(stmt, Return):
                        # If return is encountered, stop execution
                        return stmt 
            return None
        
        
        
        case For(init, condition, increment, body):
            xy = None
            e(init, env, types)  
            while e(condition, env, types): 
                if isinstance(body, Sequence):
                    for stmt in body.statements:
                        xy = e(stmt, env, types) 
                        if xy == "break":
                            return None  
                        elif xy == "continue":
                            break 
                        elif isinstance(xy,Return):
                            return xy
                        elif isinstance(stmt, Return):
                            return stmt 
                else:
                    xy = e(body, env, types)
                    if xy == "break":
                            return None  
                    elif xy == "continue":
                            continue 
                    elif isinstance(xy,Return):
                            return xy
                    elif isinstance(stmt, Return):
                        return stmt 
                e(increment, env, types)
            return xy

        case Sequence(statements):
            last_value = []
            for stmt in statements:
                last_value=e(stmt, env, types,call_stack)  
                if isinstance(last_value,Return):
                    return last_value
                elif isinstance(stmt, Return):
                    return stmt       
            return last_value
        
        case Break():
            return "break"

        case Continue():
            return "continue"

        case String(v):
            return v
        case Concat(left, right):
            left_val = e(left, env, types)
            right_val = e(right, env, types)

            if not isinstance(left_val, str) or not isinstance(right_val, str):
                raise TypeError("Concat can only be used with String")

            return left_val + right_val 
        
        case Print(values):
            results = []
            for value in values:
                result = e(value, env, types)
                if isinstance(result, bool): 
                    result = "nocap" if result else "cap"
                elif isinstance(result, int) and result < 0:
                    result = "~" + str(-result)
                results.append(result)
            # print(*results) 
            print("".join(map(str, results)))
            return None
            # results = [e(value, env, types) for value in values]
            # print(*results)  # Changed to use default print behavior with newline
           
        case Array(elements):
            return [e(element, env, types) for element in elements]            
        case ArrayAccess(array, index):
            array_val = e(array, env, types)
            index_val = e(index, env, types)
            if not isinstance(array_val, (list,str,dict)):
                raise TypeError(f"Indexing cannot be used with type {type(array_val).__name__}")
            return array_val[index_val]
        
        case ArrayAssignment(array, index, value):
            # ── multi‑index form  arr[0][1] = rhs  (index is None) ─────────
            if index is None and isinstance(array, ArrayAccess):
                idx_asts: list[AST] = []
                node = array
                while isinstance(node, ArrayAccess):
                    idx_asts.insert(0, node.index)
                    node = node.array              # walk up
                if not isinstance(node, Variable):
                    raise RuntimeError("Invalid assignment target")

                # base collection
                col = e(node, env, types)
                if not isinstance(col, (list, dict)):
                    raise TypeError("Left side must be array or hashmap")

                # walk down to parent container
                for idx_ast in idx_asts[:-1]:
                    col = col[e(idx_ast, env, types)]
                    if not isinstance(col, (list, dict)):
                        raise TypeError("Intermediate element is not a collection")

                last_idx = e(idx_asts[-1], env, types)
                col[last_idx] = e(value, env, types)
                return col[last_idx]

            # ── single‑level form  arr[i] = rhs  or  map[key] = rhs ───────
            col   = e(array, env, types)
            key   = e(index, env, types)
            val   = e(value, env, types)

            if isinstance(col, list):
                if not isinstance(key, int):
                    raise TypeError("Array index must be an integer")
                if key < 0 or key >= len(col):
                    raise IndexError(f"Index {key} out of bounds")
            elif not isinstance(col, dict):
                raise TypeError("Assignment target is neither array nor hashmap")

            col[key] = val
            return val

        case ArrayAppend(array, value):
            arr = e(array, env, types)
            if not isinstance(arr, list):
                raise TypeError("append() can only be used on arrays")
            arr.append(e(value, env, types))
            return arr                           # return the *same list* ref

        case ArrayDelete(array, index):
            col = e(array, env, types)

            if isinstance(col, list):
                idx = e(index, env, types)
                if not isinstance(idx, int):
                    raise TypeError("Array index must be an integer")
                if idx < 0 or idx >= len(col):
                    raise IndexError(f"Index {idx} out of bounds")
                del col[idx]
                return col

            if isinstance(col, dict):
                key = e(index, env, types)
                if key not in col:
                    raise KeyError(f"Key {key} not found in hashmap")
                del col[key]
                return col

            raise TypeError("delete() can only be used on arrays or hashmaps")

        case ArrayLength(array):
            col = e(array, env, types)
            if isinstance(col, (list, dict)):
                return len(col)
            raise TypeError("len() can only be used on arrays or hashmaps")
                    
        case HashMap(name,key_type, value_type):
            env[name] = {}  
            types[name] = f"hashmap<{key_type}, {value_type}>"
            return None     

            
        case StackDeclaration(element_type, name):
            env[name] = Stack()  # Initialize an empty stack
            types[name] = f"stack<{element_type}>"
            return None
        
        case StackPush(stack_name, value):
            if stack_name not in env:
                raise NameError(f"Undefined stack: {stack_name}")
            stack = env[stack_name]
            if not isinstance(stack, Stack):
                raise TypeError(f"{stack_name} is not a stack")
            val = e(value, env, types)
            # Get the element type from the stack type
            element_type = types[stack_name].split('<')[1][:-1]  # Extract type between < and >
            if not isinstance(val, datatypes[element_type]):
                raise TypeError(f"Cannot push {type(val).__name__} to stack of {element_type}")
            stack.push(val)
            return None 
        
        case StackPop(stack_name):
            if stack_name not in env:
                raise NameError(f"Undefined stack: {stack_name}")
            stack = env[stack_name]
            if not isinstance(stack, Stack):
                raise TypeError(f"{stack_name} is not a stack")
            stack.pop()  
            return None
        
        case StackTop(stack_name):
            if stack_name not in env:
                raise NameError(f"Undefined stack: {stack_name}")
            stack = env[stack_name]
            if not isinstance(stack, Stack):
                raise TypeError(f"{stack_name} is not a stack")
            return stack.top()
        
        case QueueDeclaration(element_type, name):
            env[name] = Queue()  # Initialize an empty queue
            types[name] = f"queue<{element_type}>"
            return None

        case QueuePush(queue_name, value):
            if queue_name not in env:
                raise NameError(f"Undefined queue: {queue_name}")
            queue = env[queue_name]
            if not isinstance(queue, Queue):
                raise TypeError(f"{queue_name} is not a queue")
            val = e(value, env, types)
            # Get the element type from the queue type
            element_type = types[queue_name].split('<')[1][:-1]  # Extract type between < and >
            if not isinstance(val, datatypes[element_type]):
                raise TypeError(f"Cannot push {type(val).__name__} to queue of {element_type}")
            queue.push(val)
            return None

        case QueuePop(queue_name):
            if queue_name not in env:
                raise NameError(f"Undefined queue: {queue_name}")
            queue = env[queue_name]
            if not isinstance(queue, Queue):
                raise TypeError(f"{queue_name} is not a queue")
            return queue.pop()

        case QueueFirst(queue_name):
            if queue_name not in env:
                raise NameError(f"Undefined queue: {queue_name}")
            queue = env[queue_name]
            if not isinstance(queue, Queue):
                raise TypeError(f"{queue_name} is not a queue")
            return queue.first()

