from enum import Enum
from parser import *
from stack_vm import *

class Opcode(Enum):
    """Enum for stack-based VM opcodes (standardized)"""
    PUSH = 0x01       # Push a value onto the stack (replaces LOAD)
    POP = 0x02        # Remove top value from stack
    STORE = 0x03      # Store stack value into a variable
    ADD = 0x04
    SUB = 0x05
    MUL = 0x06
    DIV = 0x07
    POW = 0x08
    NEG = 0x09
    CMP_LT = 0x0A
    CMP_GT = 0x0B
    CMP_EQ = 0x0C
    CMP_NEQ = 0x0D
    JMP = 0x0E        # Unconditional jump
    JZ = 0x0F        # Jump if Zero (False)
    JNZ = 0x10        # Jump if Not Zero (True)
    CALL = 0x11       # Call a function
    RETURN = 0x12     # Return from function
    PRINT = 0x13      # System call: Print (handled externally)
    NEWARRAY = 0x14   # Allocate new array
    NEWLINE= 0x15
    LNOT = 0x17       # Logical NOT
    DUP = 0x18        # Duplicate top of stack
    INPUT = 0x19      # System call: Read user input
    EXIT = 0x1A       # End execution (replaces HALT)
    LOAD = 0x1B
    CREATE_LIST = 0x1C
    LOAD_INDEX = 0x1D
    STORE_INDEX = 0x1E
    APPEND_INDEX = 0x1F
    DELETE_INDEX = 0x20
    MOD = 0x16
    FLR_DIV = 0x21
    
class AssemblyGenerator:
    def __init__(self):
        self.instructions = []
        self.instruction_counter = 0
        self.label_counter = 0
        self.symbol_table = {}
        self.break_labels=[]
        self.continue_labels=[]
        self.function_table = {}  # Track function definitions
        self.current_function = None  # Track current function context

    def emit(self, instruction, *args):
        """Generate a tuple-based instruction with instruction index."""
        if isinstance(instruction, str):  # Handle labels
            self.instructions.append((f"{instruction}:",))  # Single-element tuple for labels
        else:
            # print((self.instruction_counter, instruction.name, instruction.value), args)
            self.instructions.append(((self.instruction_counter, instruction.name, instruction.value) , args))
            self.instruction_counter += 1


    def generate_label(self):
        """Generate a unique label for jumps"""
        label = f"L{self.label_counter}"
        self.label_counter += 1
        return label

    def get_var_location(self, var_name):
        """Assign memory location for a variable"""
        if var_name not in self.symbol_table:
            self.symbol_table[var_name] = len(self.symbol_table)
        return self.symbol_table[var_name]

    def generate(self, ast):
        """Generate assembly for an AST"""
        self.generate_statement(ast)
        self.emit(Opcode.EXIT)  # End of program
        return  self.instructions, self.function_table 

    def generate_statement(self, expr):
        """Convert AST expressions into bytecode"""
        if isinstance(expr, Number):
            self.emit(Opcode.PUSH, expr.val)
        elif isinstance(expr, String):
            self.emit(Opcode.PUSH, expr.val)
        elif isinstance(expr, Boolean):
            self.emit(Opcode.PUSH, expr.val)
        elif isinstance(expr, Variable):
            var_loc = self.get_var_location(expr.val)
            
            # Check if this is a function reference
            if expr.val in self.function_table:
                # For function references, push the function name instead of loading a value
                self.emit(Opcode.PUSH, expr.val)
            else:
                # For regular variables, load the value
                self.emit(Opcode.LOAD, var_loc)
                
        elif isinstance(expr, Parenthesis):
            self.generate_statement(expr.expr)
        elif isinstance(expr, Input):
            self.emit(Opcode.INPUT)  # Emit input instruction  
        elif isinstance(expr, ArrayAccess):  # Handling numbers[2]
            self.generate_array_access(expr)
        elif isinstance(expr, ArrayAppend):  # Handle appending in expressions
            self.generate_array_append(expr)

        elif isinstance(expr, ArrayDelete):  # Handle deletion in expressions
            self.generate_array_delete(expr)
            
        elif isinstance(expr, BinOp):
            op_map = {
                "+": Opcode.ADD, "-": Opcode.SUB, "*": Opcode.MUL, "/": Opcode.DIV, "^": Opcode.POW,
                "<": Opcode.CMP_LT, ">": Opcode.CMP_GT, "==": Opcode.CMP_EQ, "!=": Opcode.CMP_NEQ, "%":Opcode.MOD, "//": Opcode.FLR_DIV
            }

            if expr.op == "and":
                # Generate code for the left operand
                self.generate_statement(expr.left)
                
                # Create a label to jump to if the left operand is false
                end_label = self.generate_label()
                
                # Duplicate the top value for the conditional jump
                self.emit(Opcode.DUP)
                
                # If the left operand is false (0), skip the right operand
                self.emit(Opcode.JZ, end_label)
                
                # Pop the duplicated value
                self.emit(Opcode.POP)
                
                # Generate code for the right operand
                self.generate_statement(expr.right)
                
                # Mark the end label
                self.emit(f"{end_label}:")
            
            elif expr.op == "or":
                # Generate code for the left operand
                self.generate_statement(expr.left)
                
                # Create a label to jump to if the left operand is true
                end_label = self.generate_label()
                
                # Duplicate the top value for the conditional jump
                self.emit(Opcode.DUP)
                
                # If the left operand is true (non-zero), skip the right operand
                self.emit(Opcode.JNZ, end_label)
                
                # Pop the duplicated value
                self.emit(Opcode.POP)
                
                # Generate code for the right operand
                self.generate_statement(expr.right)
                
                # Mark the end label
                self.emit(f"{end_label}:")
            
            elif expr.op == "<=":
                self.generate_statement(expr.left)
                self.generate_statement(expr.right)
                self.emit(Opcode.CMP_GT)  # a <= b → !(a > b)
                self.emit(Opcode.LNOT)
            
            elif expr.op == ">=":
                self.generate_statement(expr.left)
                self.generate_statement(expr.right)
                self.emit(Opcode.CMP_LT)  # a >= b → !(a < b)
                self.emit(Opcode.LNOT)
            
            elif expr.op in op_map:
                self.generate_statement(expr.left)
                self.generate_statement(expr.right)
                self.emit(op_map[expr.op])
            
            else:
                raise KeyError(f"Unsupported operator: '{expr.op}'")



        elif isinstance(expr, Sequence):
            for sub_expr in expr.statements:
                self.generate_statement(sub_expr )
        elif isinstance(expr, Declaration):
            self.generate_declaration(expr)
        elif isinstance(expr, Assignment):
            var_loc = self.get_var_location(expr.name)
            self.generate_statement(expr.value)  
            self.emit(Opcode.STORE, var_loc)
        elif isinstance(expr, ArrayAssignment): 
            print(":::::", expr)
            self.generate_array_store(expr)  # Store value at index
        elif isinstance(expr, Print):
            for value in expr.values:
                self.generate_statement(value)  
                self.emit(Opcode.PRINT)
            self.emit(Opcode.NEWLINE)
        elif isinstance(expr, Cond):
            self.generate_if(expr)

        elif isinstance(expr, While):
            self.generate_while(expr)

        elif isinstance(expr, For):
            self.generate_for(expr)

        elif isinstance(expr, Break):
            self.emit(Opcode.JMP, self.break_labels[-1])

        elif isinstance(expr, Continue):
            self.emit(Opcode.JMP, self.continue_labels[-1])

        elif isinstance(expr, FunctionCall):
            self.generate_function_call(expr)

        elif isinstance(expr, Function):
            self.generate_function(expr)

        elif isinstance(expr, Return):
            if isinstance(expr.value, Array):
            # Create a new array
                self.emit(Opcode.NEWARRAY, "temp")
                
                # Push each element onto the stack
                for element in expr.value.elements:
                    self.generate_statement(element)
                
                # Create the array from stack items
                self.emit(Opcode.CREATE_LIST, len(expr.value.elements))
            else:
                # For non-array return values
                self.generate_statement(expr.value)
            
            self.emit(Opcode.RETURN)

        else:
            self.generate_statement(expr) 

        
    def generate_if(self, expr):
        """Generate assembly for if-else statement with multiple elif support"""
        end_label = self.generate_label()  # Label for the end of the entire if-structure
        
        # Generate code for the initial 'if' condition and body
        self.generate_statement(expr.If[0])
        first_elif_or_else_label = self.generate_label()
        self.emit(Opcode.JZ, first_elif_or_else_label)  # Jump to next condition if false
        
        self.generate_statement(expr.If[1])
        self.emit(Opcode.JMP, end_label)  # Skip all remaining conditions after executing body
        
        self.emit(f"{first_elif_or_else_label}:")
        
        # Generate code for each 'elif' condition and body
        if expr.Elif:
            for i, (elif_cond, elif_body) in enumerate(expr.Elif):
                self.generate_statement(elif_cond)
                
                # If this is the last elif and there's no else, jump to end if false
                # Otherwise, jump to the next elif or else
                next_label = end_label if i == len(expr.Elif) - 1 and not expr.Else else self.generate_label()
                
                self.emit(Opcode.JZ, next_label)  # Jump to next condition if false
                self.generate_statement(elif_body)
                self.emit(Opcode.JMP, end_label)  # Skip to end after executing body
                
                if next_label != end_label:
                    self.emit(f"{next_label}:")
        
        # Generate code for the 'else' body if it exists
        if expr.Else:
            self.generate_statement(expr.Else)
        
        # This is where execution continues after the if-elif-else structure
        self.emit(f"{end_label}:")


    def generate_while(self, expr):
        """Generate assembly for while loops"""
        start_label = self.generate_label()
        end_label = self.generate_label()
        self.break_labels.append(end_label)
        self.continue_labels.append(start_label)
        self.emit(f"{start_label}:")
        self.generate_statement(expr.condition)
        self.emit(Opcode.JZ, end_label)

        self.generate_statement(expr.body)
        self.emit(Opcode.JMP, start_label)

        self.emit(f"{end_label}:")
        self.break_labels.pop()
        self.continue_labels.pop()

    def generate_for(self, expr):
        """Generate assembly for for loops"""
        self.generate_statement(expr.init)

        start_label = self.generate_label()
        end_label = self.generate_label()
        self.break_labels.append(end_label)
        self.continue_labels.append(start_label)
        increment_label = self.generate_label()
        self.emit(f"{start_label}:")
        self.generate_statement(expr.condition)
        self.emit(Opcode.JZ, end_label)

        self.generate_statement(expr.body)
        self.emit(f"{increment_label}:")
        self.generate_statement(expr.increment)
        self.emit(Opcode.JMP, start_label)

        self.emit(f"{end_label}:")
        self.break_labels.pop()
        self.continue_labels.pop()

    def generate_declaration(self, decl):
        """Convert AST variable declarations into bytecode"""
        var_loc = self.get_var_location(decl.name)
        print(decl.value)
        if decl.type == 'fn':
            # For function type declarations, handle specially
            self.generate_statement(decl.value)  # This will push the function name
            self.emit(Opcode.STORE, var_loc)
        elif isinstance(decl.value, Array):
            self.emit(Opcode.NEWARRAY, decl.name)  # Allocate array space

            for element in decl.value.elements:
                self.generate_statement(element)  # Push each element onto the stack
            
            self.emit(Opcode.CREATE_LIST, len(decl.value.elements))  # Create list from stack items
            self.emit(Opcode.STORE, var_loc)  # Store the array in the variable
        else:
            self.generate_statement(decl.value)
            self.emit(Opcode.STORE, var_loc)

    def generate_array_access(self, array_access):
        """Handles array indexing (arr[i])"""
        var_loc = self.get_var_location(array_access.array.val)  
        self.generate_statement(array_access.index)  # Push index onto stack
        self.emit(Opcode.LOAD_INDEX, var_loc)  # Load element from array

    def generate_array_store(self, array_store):
        """Handles writing to an array (arr[i] = value)"""
        var_loc = self.get_var_location(array_store.array.val)
        
        self.generate_statement(array_store.index)  # Push index
        self.generate_statement(array_store.value)  # Push value
        self.emit(Opcode.STORE_INDEX, var_loc)  # Store in array

    def generate_array_append(self, append_node):
        """Generate bytecode for appending to an array"""
        array_loc = self.get_var_location(append_node.array.val) 
        self.generate_statement(append_node.value)  # Then push value to append
        self.emit(Opcode.APPEND_INDEX, array_loc)              # Append value to array
    
    def generate_array_delete(self, delete_node):
        """Generate bytecode for deleting from an array"""
        array_loc = self.get_var_location(delete_node.array.val)
        self.generate_statement(delete_node.index)  # Push index to delete
        self.emit(Opcode.DELETE_INDEX, array_loc)              # Delete element at index

    def print_assembly(self):
        """Print generated assembly code"""
        for line in self.instructions:
            # print(line)
            print(line[0][0], line[0][1], line[1])
            
           
    def generate_function(self, expr):
        """Generate assembly for function definition"""
        # Store function name
        func_name = expr.name
        
        # Create a label for the function
        func_label = self.generate_label()
        
        # Save the current symbol table
        old_symbol_table = self.symbol_table.copy()
        
        # Reset the symbol table for the function scope
        self.symbol_table = {}
        
        # Pre-allocate locations for parameters
        param_locations = []
        for param_type, param_name in expr.params:
            param_loc = self.get_var_location(param_name)
            param_locations.append(param_name)
        
        self.function_table[func_name] = {
            'label': func_label,
            'params': param_locations,
            'return_type': expr.return_type if hasattr(expr, 'return_type') else None
        }
        
        # Jump past the function definition during normal execution
        end_func_label = self.generate_label()
        self.emit(Opcode.JMP, end_func_label)
        
        # Function entry point
        self.emit(f"{func_label}:")
        
        # Save current function context
        prev_function = self.current_function
        self.current_function = func_name
        
        # Generate code for function body
        self.generate_statement(expr.body)
        
        # If no explicit return at the end, add one with None value
        if not isinstance(expr.body, Return) and not (
                isinstance(expr.body, Sequence) and 
                expr.body.statements and 
                isinstance(expr.body.statements[-1], Return)):
            self.emit(Opcode.PUSH, None)  # Push None as default return value
            self.emit(Opcode.RETURN)
        
        # Restore previous function context
        self.current_function = prev_function
        
        # Restore the previous symbol table
        self.symbol_table = old_symbol_table
        
        # End of function definition
        self.emit(f"{end_func_label}:")

    def generate_function_call(self, call_node):
        """Generate assembly for function call"""
        # Push arguments onto stack in order
        for arg in call_node.params:
            self.generate_statement(arg)
        
        # Call the function
        self.emit(Opcode.CALL, call_node.name)
        
# with open('bytecode_tests.txt', 'r', encoding='utf-8') as file:
with open('sample_code.yap', 'r', encoding='utf-8') as file:
        source_code = file.read()
ast = parse(source_code)
# print(ast)
generator = AssemblyGenerator()
abc, function_table = generator.generate(ast)
# print(abc)
# print(generator.function_table)
# Print human-readable assembly
# generator.print_assembly()
vm = StackVM(abc, function_table)
# print("ok")
vm.run()



