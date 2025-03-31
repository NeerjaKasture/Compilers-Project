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
        case Input(inp_type):
            try:
                user_input = input()
                match inp_type:
                    case "int":
                        return int(user_input)
                    case "float":
                        return float(user_input)
                    case "string":
                        return str(user_input)
                    case _:
                        raise TypeError(f"Unsupported input type: {inp_type}")
            except ValueError as ve:
                print(f"Invalid input for type {inp_type}: {ve}")
                return None
            
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
                
                if not isinstance(arg_value, datatypes[param_type]):
                    raise TypeError(f"Argument '{param_name}' must be of type {param_type}")

                local_env[param_name] = arg_value
                local_types[param_name] = param_type 
            
            call_stack.append((local_env,local_types))   
            if(len(call_stack)>MAX_RECURSION_DEPTH):
                raise RecursionLimitError(name)
            result = e(func.body, local_env, local_types,call_stack)
            result=e(result)
            if func.return_type != "void" and not isinstance(result, datatypes[func.return_type]):
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
                if op in {"+", "-", "*", "/", "%", "^","<",">","<=",">=","&","|","~~"}:
                    raise TypeError(f"Cannot apply '{op}' to Boolean type")
                match op:
                    case "and":
                        return e(l) and e(r)
                    case "or":
                        return e(l) or e(r)
                    case "not":
                        return not e(r)
            if isinstance(e(l), str) or isinstance(e(r), str):
                if op in {"+", "-", "*", "/", "%", "^","<",">","<=",">=","&","|","~~"}:
                    raise TypeError(f"Cannot apply '{op}' to String type")  
            match op:
                case "+":
                    left_val = e(l)
                    right_val = e(r)
                    if not (isinstance(left_val, (int, float)) and isinstance(right_val, (int, float))):
                        raise TypeError("Addition (+) is only supported between numbers (int/float)")
                    return left_val + right_val
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
            
            local_env=env; local_types=types
            if call_stack:
                local_env,local_types = call_stack[-1]
            
            val = e(value, local_env, local_types)
            if val is None:  # Handle failed input
                raise ValueError(f"Failed to get valid input for {var_name}")
            if is_array_type(var_type):
                if not isinstance(val, list):
                    raise TypeError(f"Variable '{var_name}' must be of type {var_type}")
                # Check that all elements are of the base type
                base_type = datatypes[get_base_type(var_type)]
                if not all(isinstance(x, base_type) for x in val):
                    raise TypeError(f"All elements in array '{var_name}' must be of type {get_base_type(var_type)}")
            elif not isinstance(val, datatypes[var_type]):
                
                raise TypeError(f"Variable '{var_name}' must be of type {var_type}")

            local_env[var_name] = val

            # is this ok to store type of python itself and not a string?
            local_types[var_name] = var_type


            return 
        
        case Assignment(var_name, value):
            
            local_env=env; local_types=types
            if call_stack:
                local_env,local_types = call_stack[-1]

            if var_name not in local_env:
                raise NameError(f"Undefined variable: {var_name}")

            val = e(value, local_env, types)

            if not isinstance(val, datatypes[local_types[var_name]]):
                raise TypeError(f"Variable '{var_name}' must be of type {local_types[var_name]}")

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
                results.append(result)
            # print(*results)  # This will print the values
            print("".join(map(str, results))) # this will print the values without adding extra space while printing
            return None
            # results = [e(value, env, types) for value in values]
            # print(*results)  # Changed to use default print behavior with newline
            # return None
        case Array(elements):
            return [e(element, env, types) for element in elements]
        case ArrayAccess(array, index):
            array_val = e(array, env, types)
            index_val = e(index, env, types)
            if not isinstance(array_val, (list,str)):
                raise TypeError("Only arrays and strings can be indexed")
            return array_val[index_val]
        case ArrayAssignment(array, index, value):
            array_val = e(array, env, types)
            index_val = e(index, env, types)
            value_val = e(value, env, types)
            if not isinstance(array_val, (list,str)):
                raise TypeError("Array assignment can only be used with arrays")
            
            array_val[index_val] = value_val
            return value_val
        case ArrayAppend(array, value):
            array_name = array.val  # Get the variable name
            if array_name in env and isinstance(env[array_name], list):
                env[array_name].append(e(value, env, types))  # Append the new value
                return env[array_name]  # Return the updated array
            else:
                raise TypeError(f"Cannot append to non-array type: {array_name}")
        case ArrayDelete(array, index):
            array_name = array.val  # Get the variable name
            if array_name in env and isinstance(env[array_name], list):
                index_val = e(index, env, types)  # Evaluate the index
                if not isinstance(index_val, int):
                    raise TypeError(f"Array index must be an integer, got {type(index_val).__name__}")
                if index_val < 0 or index_val >= len(env[array_name]):
                    raise IndexError(f"Index {index_val} out of bounds for array '{array_name}'")
                
                del env[array_name][index_val]  # Remove the element at index
                return env[array_name]  # Return updated array
            else:
                raise TypeError(f"Cannot delete from non-array type: {array_name}")
        case StackDeclaration(element_type, name):
            if name in env:
                raise NameError(f"Stack '{name}' already declared")
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
            if name in env:
                raise NameError(f"Queue '{name}' already declared")
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

