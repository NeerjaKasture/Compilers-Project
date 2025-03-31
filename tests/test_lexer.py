import pytest
import sys
import os

# Add the project root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from lexer import lex, NumberToken, ParenthesisToken, KeywordToken, OperatorToken, BooleanToken, StringToken, VariableToken, TypeToken, SymbolToken

def test_lex_keywords():
    tokens = list(lex("if else while yeet")) 
    assert tokens == [KeywordToken("if"), KeywordToken("else"), KeywordToken("while"), KeywordToken("yeet")]

def test_lex_datatypes():
    tokens = list(lex("int float string"))
    assert tokens == [TypeToken("int"), TypeToken("float"), TypeToken("string")]

def test_lex_numbers():
    tokens = list(lex("42 3.14 0.001"))
    assert tokens == [NumberToken("42"), NumberToken("3.14"), NumberToken("0.001")]

def test_lex_operators():
    tokens = list(lex("+ - * / ^ == != <= >="))
    assert tokens == [
        OperatorToken("+"), OperatorToken("-"), OperatorToken("*"), OperatorToken("/"),
        OperatorToken("^"), OperatorToken("=="), OperatorToken("!="), 
        OperatorToken("<="), OperatorToken(">=")
    ]

def test_lex_parentheses():
    tokens = list(lex("(){}[]"))
    assert tokens == [
        ParenthesisToken("("), ParenthesisToken(")"),
        ParenthesisToken("{"), ParenthesisToken("}"),
        ParenthesisToken("["), ParenthesisToken("]")
    ]

def test_lex_booleans():
    tokens = list(lex("nocap cap"))
    assert tokens == [BooleanToken("nocap"), BooleanToken("cap")]

def test_lex_strings():
    tokens = list(lex('"Hello World" "Test String"'))
    assert tokens == [StringToken("Hello World"), StringToken("Test String")]

def test_lex_variable():
    tokens = list(lex("x y_var foo.bar"))
    assert tokens == [VariableToken("x"), VariableToken("y_var"), VariableToken("foo.bar")]

def test_lex_symbol():
    tokens = list(lex("->"))
    assert tokens == [SymbolToken("->")]

def test_lex_comments():
    tokens = list(lex("# This is a comment\nint x = 10;"))
    assert tokens == [TypeToken("int"), VariableToken("x"), OperatorToken("="), NumberToken("10"), SymbolToken(";")]

def test_lex_whitespace_and_empty():
    """Test lexing an empty string and whitespace-only string."""
    assert list(lex("")) == []
    assert list(lex("    ")) == []

def test_lex_bitwise_operators():
    """Test bitwise operators & and |"""
    tokens = list(lex("& | and"))
    assert tokens == [OperatorToken("&"), OperatorToken("|"), OperatorToken("and")]

def test_lex_invalid_character():
    """Test lexing an invalid character like '@' should raise SyntaxError"""
    with pytest.raises(ValueError, match="Unexpected character: @"):
        list(lex("@"))
