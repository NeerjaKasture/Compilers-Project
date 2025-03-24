from enum import Enum
from parser import *

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
    AASTORE = 0x15    # Store into array
    AALOAD = 0x16     # Load from array
    LNOT = 0x17       # Logical NOT
    DUP = 0x18        # Duplicate top of stack
    INPUT = 0x19      # System call: Read user input
    EXIT = 0x1A       # End execution (replaces HALT)

class AssemblyGenerator:
    def __init__(self):
        self.instructions = []
        self.instruction_counter = 0
        self.label_counter = 0
        self.symbol_table = {}

    def emit(self, instruction, *args):
        """Generate a formatted assembly instruction."""
        args_str = " ".join(map(str, args)) if args else ""
        self.instructions.append(f"{self.instruction_counter}: {instruction.name:<10} {args_str}")
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
        if isinstance(ast, Sequence):
            for stmt in ast.statements:
                self.generate_statement(stmt)
        else:
            self.generate_statement(ast)
        self.emit(Opcode.EXIT)  # End of program

    def generate_expression(self, expr):
        """Convert AST expressions into bytecode"""
        if isinstance(expr, Number):
            self.emit(Opcode.PUSH, expr.val)

        elif isinstance(expr, Variable):
            var_loc = self.get_var_location(expr.val)
            self.emit(Opcode.PUSH, var_loc)
        elif isinstance(expr, Parenthesis):
            self.generate_expression(expr.expr)
        elif isinstance(expr, BinOp):
            self.generate_expression(expr.left)
            self.generate_expression(expr.right)

            op_map = {
                "+": Opcode.ADD, "-": Opcode.SUB, "*": Opcode.MUL, "/": Opcode.DIV, "^": Opcode.POW,
                "<": Opcode.CMP_LT, ">": Opcode.CMP_GT, "==": Opcode.CMP_EQ, "!=": Opcode.CMP_NEQ,
            }

            if expr.op in op_map:
                self.emit(op_map[expr.op])

            elif expr.op == "<=":
                self.emit(Opcode.CMP_GT)  # a <= b → !(a > b)
                self.emit(Opcode.LNOT)  

            elif expr.op == ">=":
                self.emit(Opcode.CMP_LT)  # a >= b → !(a < b)
                self.emit(Opcode.LNOT)

            else:
                raise KeyError(f"Unsupported operator: '{expr.op}'")


    def generate_statement(self, stmt):
        """Convert AST statements into bytecode"""
        if isinstance(stmt, Assignment):
            var_loc = self.get_var_location(stmt.name)
            self.generate_expression(stmt.value)  # ✅ Use `generate_expression()`
            self.emit(Opcode.STORE, var_loc)

        elif isinstance(stmt, Print):
            for value in stmt.values:
                self.generate_expression(value)  # ✅ Use `generate_expression()`
                self.emit(Opcode.PRINT)

        elif isinstance(stmt, Cond):
            self.generate_if(stmt)

        elif isinstance(stmt, While):
            self.generate_while(stmt)

        elif isinstance(stmt, For):
            self.generate_for(stmt)

        elif isinstance(stmt, Break):
            self.emit(Opcode.JMP, "BREAK_LABEL")

        elif isinstance(stmt, Continue):
            self.emit(Opcode.JMP, "CONTINUE_LABEL")

        elif isinstance(stmt, FunctionCall):
            for arg in stmt.params:
                self.generate_expression(arg)
            self.emit(Opcode.CALL, stmt.name)

        elif isinstance(stmt, Function):
            self.emit(Opcode.CALL, stmt.name)

        elif isinstance(stmt, Return):
            self.generate_expression(stmt.value)  # ✅ Use `generate_expression()`
            self.emit(Opcode.RETURN)

        else:
            self.generate_expression(stmt)  # ✅ Handle any leftover expressions


    def generate_if(self, stmt):
        """Generate assembly for if-else statement"""
        else_label = self.generate_label()
        end_label = self.generate_label()

        self.generate_expression(stmt.If[0])
        self.emit(Opcode.JZ, else_label)

        self.generate_statement(stmt.If[1])
        self.emit(Opcode.JMP, end_label)

        self.emit(f"{else_label}:")
        if stmt.Else:
            self.generate_statement(stmt.Else)

        self.emit(f"{end_label}:")

    def generate_while(self, stmt):
        """Generate assembly for while loops"""
        start_label = self.generate_label()
        end_label = self.generate_label()

        self.emit(f"{start_label}:")
        self.generate_expression(stmt.condition)
        self.emit(Opcode.JZ, end_label)

        self.generate_statement(stmt.body)
        self.emit(Opcode.JMP, start_label)

        self.emit(f"{end_label}:")

    def generate_for(self, stmt):
        """Generate assembly for for loops"""
        self.generate_statement(stmt.init)

        start_label = self.generate_label()
        end_label = self.generate_label()
        increment_label = self.generate_label()
        self.emit(f"{start_label}:")
        self.generate_expression(stmt.condition)
        self.emit(Opcode.JZ, end_label)

        self.generate_statement(stmt.body)
        self.emit(f"{increment_label}:")
        self.generate_statement(stmt.increment)
        self.emit(Opcode.JMP, start_label)

        self.emit(f"{end_label}:")

    
    def print_assembly(self):
        """Print generated assembly code"""
        for line in self.instructions:
            print(line)


# Example usage:

with open('sample_code.txt', 'r', encoding='utf-8') as file:
        source_code = file.read()
ast = parse(source_code)
print(ast)
generator = AssemblyGenerator()
generator.generate(ast)

# Print human-readable assembly
generator.print_assembly()

# source_code = "int[] arr = [1, 2, 3]; print(arr[2]);"


