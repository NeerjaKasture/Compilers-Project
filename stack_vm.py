def get_true_val(word):
    if isinstance(word, str):
        if word.count('.') == 1:
            parts = word.split('.')
            if len(parts) == 2 and all(part.lstrip('-').isdigit() for part in parts):
                return float(word)
        elif word.lstrip('-').isdigit():
            return int(word)
    return word


class StackVM:
    def __init__(self, instructions, function_table):
        self.instructions = instructions
        self.stack = []
        self.env_stack = [[None] * 16]  # Start with one scope of 16 slots
        self.call_stack = []
        self.labels = self._map_labels()
        self.pc = 0
        self.print_buffer = []
        self.function_table = function_table
        # print(function_table)
        
    def _map_labels(self):
        labels = {}
        for i, instr in enumerate(self.instructions):
            if isinstance(instr, tuple) and len(instr) == 1 and isinstance(instr[0], str) and instr[0].endswith("::"):
                label = instr[0][:-2]  # Remove the "::"
                labels[label] = i + 1  # Point to the next instruction
        # print("labels", labels)
        return labels

    def push_env(self, size=16):
        self.env_stack.append([None] * size)

    def pop_env(self):
        self.env_stack.pop()

    def set_var(self, index, value):
        env = self.env_stack[-1]
        if index >= len(env):
            env.extend([None] * (index - len(env) + 1))
        env[index] = value

    def get_var(self, index):
        return self.env_stack[-1][index]

    def run(self):
        while self.pc < len(self.instructions):
            instr = self.instructions[self.pc]
            # print(instr)
            if isinstance(instr[0], str) and instr[0].endswith("::"):
                self.pc += 1
                continue

            count, instr_name, op = instr[0]
            args = instr[1]

            if op == 0x01:  # PUSH
                self.stack.append(get_true_val(args[0]))

            elif op == 0x02:  # POP
                self.stack.pop()

            elif op == 0x18:  # DUP
                self.stack.append(self.stack[-1])

            elif op == 0x04:  # ADD
                b, a = self.stack.pop(), self.stack.pop()
                self.stack.append(a + b)

            elif op == 0x05:  # SUB
                b, a = self.stack.pop(), self.stack.pop()
                self.stack.append(a - b)

            elif op == 0x06:  # MUL
                b, a = self.stack.pop(), self.stack.pop()
                self.stack.append(a * b)

            elif op == 0x07:  # DIV
                b, a = self.stack.pop(), self.stack.pop()
                self.stack.append(a / b)

            elif op == 0x09:  # NEG
                self.stack.append(-self.stack.pop())

            elif op == 0x08:  # POW
                b, a = self.stack.pop(), self.stack.pop()
                self.stack.append(a ** b)
            elif op == 0x16: #MODULO
                b, a = self.stack.pop(), self.stack.pop()
                self.stack.append(a % b)
            elif op == 0x21: #Floor division
                b, a = self.stack.pop(), self.stack.pop()
                self.stack.append(a // b)
            elif op == 0x17: #LNOT
                curr = self.stack.pop()
                if curr == "nocap":
                    self.stack.append("cap")
                else:
                    self.stack.append("nocap")
            elif op == 0x0C:  # CMP_EQ
                b, a = self.stack.pop(), self.stack.pop()
                if (a==b):
                   self.stack.append("nocap")
                else:
                    self.stack.append("cap")

            elif op == 0x0A:  # CMP_LT
                b, a = self.stack.pop(), self.stack.pop()
                if (a<b):
                   self.stack.append("nocap")
                else:
                    self.stack.append("cap")

            elif op == 0x0B:  # CMP_GT
                b, a = self.stack.pop(), self.stack.pop()
                if (a>b):
                   self.stack.append("nocap")
                else:
                    self.stack.append("cap")
            elif op == 0x0D:  # CMP_NEQ
                b, a = self.stack.pop(), self.stack.pop()
                if (a!=b):
                   self.stack.append("nocap")
                else:
                    self.stack.append("cap")
                
            elif op == 0x1B:  # LOAD
                index = args[0]
                self.stack.append(self.get_var(index))

            elif op == 0x03:  # STORE
                index = args[0]
                self.set_var(index, self.stack.pop())

            elif op == 0x0E:  # JMP
                self.pc = self.labels[args[0]]
                continue

            elif op == 0x0F:  # JZ
                if self.stack.pop() == "cap":
                    self.pc = self.labels[args[0]]
                    continue

            elif op == 0x10:  # JNZ
                if self.stack.pop() != "cap":
                    self.pc = self.labels[args[0]]
                    continue

            elif op == 0x11:  # CALL
                func_name = args[0]
                func_data = self.function_table[func_name]
                func_label = func_data['label']
                param_count = len(func_data['params'])
                # print(func_name, func_data, func_label, param_count, self.stack)
                # Extract arguments from stack (in reverse order)
                args_for_func = [self.stack.pop() for _ in range(param_count)][::-1]

                self.call_stack.append(self.pc + 1)
                self.push_env()

                # Store args in new scope
                for i, val in enumerate(args_for_func):
                    self.set_var(i, val)

                self.pc = self.labels[func_label]
                continue

            elif op == 0x12:  # RETURN
                self.pop_env()
                self.pc = self.call_stack.pop()
                continue

            elif op == 0x13:  # PRINT
                val = self.stack.pop()

                def format_val(v):
                    if isinstance(v, (int, float)):
                        return "~" + str(abs(v)) if v < 0 else str(v)
                    elif isinstance(v, list):
                        return "[" + ", ".join(format_val(x) for x in v) + "]"
                    elif isinstance(v, dict):
                        return "{" + ", ".join(f"{format_val(k)}: {format_val(vv)}" for k, vv in v.items()) + "}"
                    else:
                        return str(v)

                self.print_buffer.append(format_val(val))

                
            elif op == 0x19: #INPUT
                user_input = input()
                self.stack.append(get_true_val(user_input))
            
            elif op == 0x1A:  # EXIT
                break
            
            elif op == 0x1C: #CREATE_LIST
                leng = args[0]
                arr =[]
                for _ in range(leng):
                    arr.append(self.stack.pop())
                self.stack.append(arr[::-1])
             
            elif op == 0x1D:  #LOAD_INDEX
                index = self.stack.pop()
                arr = self.get_var(args[0])
                self.stack.append(arr[index]) 
            
            elif op == 0x1E:  #STORE_INDEX
                val = self.stack.pop()
                index = self.stack.pop()
                arr = self.get_var(args[0])
                arr[index]=val 
                self.set_var(args[0], arr)
            
            elif op == 0x1F:  #APPEND_INDEX
                val = self.stack.pop()
                arr = self.stack.pop()
                arr.append(val)
                # self.set_var(args[0], arr)
            
            elif op == 0x20:  #DELETE_INDEX
                index = self.stack.pop()
                arr = self.stack.pop()
                del arr[index]
                # self.set_var(args[0], arr)
                     
            elif op == 0x15: #NEWLINE
                print(' '.join(self.print_buffer))
                self.print_buffer.clear()
            
            elif op== 0x22: #NEWHASH
                self.stack.append({})
                
            elif op ==0x23: #LEN
                arr = self.stack.pop()
                self.stack.append(len(arr))

            elif op == 0x24:  # CALL_INDIRECT
                func_label = self.stack.pop()  # the label was pushed on the stack by LOAD

                # You must find the function info by label!
                # Let's find it:
                func_name = None
                for name, data in self.function_table.items():
                    if data['label'] == func_label:
                        func_name = name
                        break
                if func_name is None:
                    raise Exception(f"Function label '{func_label}' not found in function_table")

                func_data = self.function_table[func_name]
                param_count = len(func_data['params'])
                
                # Pop parameters (just like normal CALL)
                args_for_func = [self.stack.pop() for _ in range(param_count)][::-1]

                self.call_stack.append(self.pc + 1)
                self.push_env()

                for i, val in enumerate(args_for_func):
                    self.set_var(i, val)

                self.pc = self.labels[func_label]
                continue

            elif op == 0x25:                    # IDX_GET
                idx = self.stack.pop()
                col = self.stack.pop()
                self.stack.append(col[idx])

            elif op == 0x26:                    # IDX_SET
                val = self.stack.pop()
                idx = self.stack.pop()
                col = self.stack.pop()
                col[idx] = val
                self.stack.append(val)          # leave RHS on stack

            self.pc += 1
