from dataclasses import dataclass, field
from collections.abc import Iterator
from keywords import keywords, datatypes

@dataclass
class Token:
    # pass
    val: str
    line: int = field(default=-1)

@dataclass
class NumberToken(Token):
    val: str
    def __eq__(self, other):
        return isinstance(other, NumberToken) and self.val == other.val

@dataclass
class ParenthesisToken(Token):
    val: str
    def __eq__(self, other):
        return isinstance(other, ParenthesisToken) and self.val == other.val

@dataclass
class KeywordToken(Token):
    val: str
    def __eq__(self, other):
        return isinstance(other, KeywordToken) and self.val == other.val

@dataclass
class OperatorToken(Token):
    val: str
    def __eq__(self, other):
        return isinstance(other, OperatorToken) and self.val == other.val

@dataclass
class BooleanToken(Token):
    val: str
    def __eq__(self, other):
        return isinstance(other, BooleanToken) and self.val == other.val

@dataclass
class StringToken(Token):
    val: str
    def __eq__(self, other):
        return isinstance(other, StringToken) and self.val == other.val

@dataclass
class VariableToken(Token):
    val: str
    def __eq__(self, other):
        return isinstance(other, VariableToken) and self.val == other.val

@dataclass
class TypeToken(Token):
    val: str
    def __eq__(self, other):
        return isinstance(other, TypeToken) and self.val == other.val

@dataclass
class SymbolToken(Token):
    val: str
    def __eq__(self, other):
        return isinstance(other, SymbolToken) and self.val == other.val


def lex(s: str) -> Iterator[Token]:
    i = 0
    line = 1

    while i < len(s):
        while i < len(s) and s[i].isspace():
            if s[i] == '\n':
                line += 1
            i += 1

        if i >= len(s):
            return            

        if s[i].isalpha():
            start = i
            while i < len(s) and (s[i].isalnum() or s[i] == '_' or s[i] == '.'):
                i += 1
            word = s[start:i]
            if word in datatypes.keys():
                yield TypeToken(word, line)
            elif word in keywords:
                if word in ["nocap", "cap"]:
                    yield BooleanToken(word, line)
                elif word in ["and", "or", "not"]:
                    yield OperatorToken(word, line)
                else:
                    yield KeywordToken(word, line)
            else:
                yield VariableToken(word, line)

        elif s[i].isdigit():
            t = s[i]
            i += 1
            has_decimal = False
            while i < len(s) and (s[i].isdigit() or (s[i] == '.' and not has_decimal)):
                if s[i] == '.':
                    has_decimal = True
                t += s[i]
                i += 1
            yield NumberToken(t, line)

        elif s[i] == '"':
            i += 1
            start = i
            while i < len(s) and s[i] != '"':
                i += 1
            yield StringToken(s[start:i], line)
            i += 1
        
        elif s[i] == '#':
            while i < len(s) and s[i] != '\n':
                i += 1
            continue


        else:
            match s[i]:
                case '.' | '+' | '*' | '-' | '/' | '%' | '^' | '(' | ')' | '<' | '>' | '=' | '!' | '~' | '{' | '}' | ';' | ',' | '[' | ']' | '->'|'%':
                    if i + 1 < len(s):
                        two_char_op = s[i:i + 2]
                        if two_char_op in {"<=", ">=", "==", "!=","~~"}:  # Explicitly handle <=, >=
                            yield OperatorToken(two_char_op, line)
                            i += 2
                            continue
                    if s[i] in "}(){[]":
                        yield ParenthesisToken(s[i], line)
                    # Handle square brackets (array access)
                    elif s[i] == '[' or s[i] == ']':
                        yield ParenthesisToken(s[i], line)
                        i += 1
                    # Handle dot notation for method calls (e.g., arr.append(2))
                    elif s[i] == '.':
                        yield SymbolToken('.', line)
                        i += 1
                        continue
                    elif s[i] == '-' and i + 1 < len(s) and s[i + 1] == '>':
                        yield SymbolToken('->', line)
                        i += 1
                    elif s[i] == '/' and i + 1 < len(s) and s[i + 1] == '/':
                        yield OperatorToken('//', line)
                        i += 1
                        
                    elif s[i] in '+ * / - ^ ~><= %':
                        yield OperatorToken(s[i], line)
                    else:
                        yield SymbolToken(s[i], line)
                    i += 1
                # Handle bitwise operators separately
                case '&' | '|':
                    yield OperatorToken(s[i], line)
                    i += 1
                case _:
                    raise ValueError(f"Unexpected character: {s[i]} at line {line}")

