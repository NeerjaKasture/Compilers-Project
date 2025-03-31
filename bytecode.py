from parser import *

class BytecodeGenerator:
    def __init__(self):
        self.bytecode = []
        self.label_counter = 0
        self.current_function = None
        self.symbol_table = {}
        self.string_pool = {}
        self.string_counter = 0

    def generate_label(self):
        """Generate a unique label for jumps"""
        label = f"L{self.label_counter}"
        self.label_counter += 1
        return label

    def emit(self, instruction, *args):
        """Add an instruction to the bytecode"""
        self.bytecode.append((instruction, args))

    def get_string_id(self, string_value):
        """Get or create an ID for a string constant"""
        if string_value not in self.string_pool:
            self.string_pool[string_value] = f"str_{self.string_counter}"
            self.string_counter += 1
        return self.string_pool[string_value]

    def generate(self, ast):
        """Generate bytecode for the entire AST"""
        if isinstance(ast, Sequence):
            for stmt in ast.statements:
                self.generate_statement(stmt)
        else:
            self.generate_statement(ast)
        
        # Add a final HALT instruction
        self.emit("HALT")
        
        return self.bytecode

    def generate_statement(self, stmt):
        """Generate bytecode for a statement"""
        if isinstance(stmt, Declaration):
            self.generate_declaration(stmt)
        elif isinstance(stmt, Assignment):
            self.generate_assignment(stmt)
        elif isinstance(stmt, ArrayAssignment):
            self.generate_array_assignment(stmt)
        elif isinstance(stmt, Function):
            self.generate_function(stmt)
        elif isinstance(stmt, FunctionCall):
            self.generate_function_call(stmt)
            # Discard the return value if not used
            self.emit("POP")
        elif isinstance(stmt, Return):
            self.generate_return(stmt)
        elif isinstance(stmt, Print):
            self.generate_print(stmt)
        elif isinstance(stmt, Cond):
            self.generate_condition(stmt)
        elif isinstance(stmt, For):
            self.generate_for_loop(stmt)
        elif isinstance(stmt, While):
            self.generate_while_loop(stmt)
        else:
            # Handle expressions that might be statements
            self.generate_expression(stmt)
            # Discard the result if it's an expression statement
            self.emit("POP")

    def generate_declaration(self, decl):
        """Generate bytecode for variable declaration"""
        var_name = decl.name
        var_type = decl.type
        
        # Add to symbol table
        self.symbol_table[var_name] = {"type": var_type}
        
        # Allocate memory for the variable
        self.emit("ALLOC", var_name, var_type)
        
        # If there's an initializer, generate code for it
        if decl.value:
            if isinstance(decl.value, Input):
                self.emit("INPUT", var_type, var_name)
            elif isinstance(decl.value, Array):
                # Create a new array
                self.emit("ARRAY_NEW", var_name, len(decl.value.elements))
                
                # Initialize array elements
                for i, element in enumerate(decl.value.elements):
                    self.generate_expression(element)
                    self.emit("ARRAY_STORE", var_name, i)
            else:
                # Generate code for the initializer expression
                self.generate_expression(decl.value)
                # Store the result in the variable
                self.emit("STORE", var_name)

    def generate_assignment(self, assign):
        """Generate bytecode for variable assignment"""
        var_name = assign.name
        
        # Generate code for the right-hand side expression
        self.generate_expression(assign.value)
        
        # Store the result in the variable
        self.emit("STORE", var_name)

    def generate_array_assignment(self, assign):
        """Generate bytecode for array element assignment"""
        # Generate code to load the array
        self.generate_expression(assign.array)
        
        # Generate code for the index expression
        self.generate_expression(assign.index)
        
        # Generate code for the value expression
        self.generate_expression(assign.value)
        
        # Store the value in the array at the index
        self.emit("ARRAY_STORE")

    def generate_function(self, func):
        """Generate bytecode for function definition"""
        func_name = func.name
        self.current_function = func_name
        
        # Create a label for the function
        func_label = f"func_{func_name}"
        
        # Emit function start
        self.emit("FUNC_BEGIN", func_name, func_label)
        
        # Jump past the function body (to avoid executing it when not called)
        end_label = self.generate_label()
        self.emit("JMP", end_label)
        
        # Function label
        self.emit(func_label + ":")
        
        # Define parameters
        for param_type, param_name in func.params:
            self.emit("PARAM", param_type, param_name)
            self.symbol_table[param_name] = {"type": param_type}
        
        # Generate code for the function body
        if func.body:
            self.generate_statement(func.body)
        
        # If no explicit return, add a default return
        if func.return_type == "void":
            self.emit("RETURN")
        
        # Function end label
        self.emit(end_label + ":")
        
        # Mark end of function
        self.emit("FUNC_END", func_name)
        
        self.current_function = None

    def generate_function_call(self, call):
        """Generate bytecode for function call"""
        func_name = call.name
        
        # Generate code for each argument
        for arg in call.args:
            self.generate_expression(arg)
        
        # Call the function
        self.emit("CALL", func_name, len(call.args))

    def generate_return(self, ret):
        """Generate bytecode for return statement"""
        # Generate code for the return expression
        if ret.expr:
            self.generate_expression(ret.expr)
        
        # Return from the function
        self.emit("RETURN")

    def generate_print(self, print_stmt):
        """Generate bytecode for print statement"""
        for value in print_stmt.values:
            self.generate_expression(value)
            self.emit("PRINT")

    def generate_condition(self, cond):
        """Generate bytecode for if/elif/else statement"""
        end_label = self.generate_label()
        
        # Generate code for the if condition
        condition, if_branch = cond.if_branch
        self.generate_expression(condition)
        
        # If condition is false, jump to the elif or else branch
        elif_label = self.generate_label()
        self.emit("JZ", elif_label)
        
        # Generate code for the if branch
        self.generate_statement(if_branch)
        
        # Jump to the end after executing the if branch
        self.emit("JMP", end_label)
        
        # Elif label
        self.emit(elif_label + ":")
        
        # Generate code for each elif branch
        for i, (elif_condition, elif_branch) in enumerate(cond.elif_branches):
            next_elif_label = self.generate_label()
            
            # Generate code for the elif condition
            self.generate_expression(elif_condition)
            
            # If condition is false, jump to the next elif or else branch
            self.emit("JZ", next_elif_label)
            
            # Generate code for the elif branch
            self.generate_statement(elif_branch)
            
            # Jump to the end after executing the elif branch
            self.emit("JMP", end_label)
            
            # Next elif label
            self.emit(next_elif_label + ":")
        
        # Generate code for the else branch if it exists
        if cond.else_branch:
            self.generate_statement(cond.else_branch)
        
        # End label
        self.emit(end_label + ":")

    def generate_for_loop(self, for_loop):
        """Generate bytecode for for loop"""
        # Generate code for initialization
        self.generate_statement(for_loop.init)
        
        # Create labels for loop condition and end
        cond_label = self.generate_label()
        end_label = self.generate_label()
        
        # Loop condition
        self.emit(cond_label + ":")
        
        # Generate code for the condition
        self.generate_expression(for_loop.condition)
        
        # If condition is false, exit the loop
        self.emit("JZ", end_label)
        
        # Generate code for the loop body
        self.generate_statement(for_loop.body)
        
        # Generate code for the increment
        self.generate_statement(for_loop.increment)
        
        # Jump back to the condition
        self.emit("JMP", cond_label)
        
        # End label
        self.emit(end_label + ":")

    def generate_while_loop(self, while_loop):
        """Generate bytecode for while loop"""
        # Create labels for loop condition and end
        cond_label = self.generate_label()
        end_label = self.generate_label()
        
        # Loop condition
        self.emit(cond_label + ":")
        
        # Generate code for the condition
        self.generate_expression(while_loop.condition)
        
        # If condition is false, exit the loop
        self.emit("JZ", end_label)
        
        # Generate code for the loop body
        self.generate_statement(while_loop.body)
        
        # Jump back to the condition
        self.emit("JMP", cond_label)
        
        # End label
        self.emit(end_label + ":")

    def generate_expression(self, expr):
        """Generate bytecode for an expression"""
        if isinstance(expr, Number):
            self.emit("LOAD", expr.val)
        elif isinstance(expr, String):
            string_id = self.get_string_id(expr.val)
            self.emit("LOAD", string_id)
        elif isinstance(expr, Boolean):
            self.emit("LOAD", 1 if expr.val else 0)
        elif isinstance(expr, Variable):
            self.emit("LOAD", expr.val)
        elif isinstance(expr, Array):
            # Create a new array
            self.emit("ARRAY_NEW", len(expr.elements))
            
            # Initialize array elements
            for i, element in enumerate(expr.elements):
                self.emit("DUP")  # Duplicate array reference
                self.emit("LOAD", i)  # Load index
                self.generate_expression(element)  # Load value
                self.emit("ARRAY_STORE")  # Store value at index
        elif isinstance(expr, ArrayAccess):
            # Generate code to load the array
            self.generate_expression(expr.array)
            
            # Generate code for the index
            self.generate_expression(expr.index)
            
            # Load the element at the index
            self.emit("ARRAY_LOAD")
        elif isinstance(expr, BinOp):
            # Special case for logical operators that need short-circuit evaluation
            if expr.op == "and":
                end_label = self.generate_label()
                self.generate_expression(expr.left)
                self.emit("DUP")  # Duplicate left result for potential short-circuit
                self.emit("JZ", end_label)  # If left is false, skip right evaluation
                self.emit("POP")  # Remove duplicate if continuing
                self.generate_expression(expr.right)
                self.emit(end_label + ":")
            elif expr.op == "or":
                end_label = self.generate_label()
                self.generate_expression(expr.left)
                self.emit("DUP")  # Duplicate left result for potential short-circuit
                self.emit("JNZ", end_label)  # If left is true, skip right evaluation
                self.emit("POP")  # Remove duplicate if continuing
                self.generate_expression(expr.right)
                self.emit(end_label + ":")
            else:
                # Generate code for the left and right operands
                self.generate_expression(expr.left)
                self.generate_expression(expr.right)
                
                # Emit the appropriate operation
                if expr.op == "+":
                    self.emit("ADD")
                elif expr.op == "-":
                    self.emit("SUB")
                elif expr.op == "*":
                    self.emit("MUL")
                elif expr.op == "/":
                    self.emit("DIV")
                elif expr.op == "^":
                    self.emit("POW")
                elif expr.op == "~":
                    self.emit("NEG")
                elif expr.op == "<":
                    self.emit("CMP_LT")
                elif expr.op == ">":
                    self.emit("CMP_GT")
                elif expr.op == "==":
                    self.emit("CMP_EQ")
                elif expr.op == "!=":
                    self.emit("CMP_NEQ")
                elif expr.op == "not":
                    self.emit("NOT")
        elif isinstance(expr, Parenthesis):
            self.generate_expression(expr.expr)
        elif isinstance(expr, FunctionCall):
            self.generate_function_call(expr)
        elif isinstance(expr, Concat):
            self.generate_expression(expr.left)
            self.generate_expression(expr.right)
            self.emit("CONCAT")
        elif isinstance(expr, Input):
            self.emit("INPUT", expr.type)

    def print_bytecode(self):
        """Print the generated bytecode in a readable format"""
        for i, (instruction, args) in enumerate(self.bytecode):
            if instruction.endswith(":"):  # Label
                print(f"{instruction}")
            else:
                print(f"{i:4d}: {instruction:10s} {', '.join(map(str, args))}")


source_code = "int[] arr = [1, 2, 3]; print(arr[2]);"
ast = parse(source_code)
generator = BytecodeGenerator()
bytecode = generator.generate(ast)
print(bytecode)
generator.print_bytecode()
