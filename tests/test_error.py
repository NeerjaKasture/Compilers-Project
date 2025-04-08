import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from parser import parse
from errors import *

def test_missing_semicolon_parse_sequence():
    source_code = """yap("hi")
    """ 

    with pytest.raises(ParseError) as excinfo:
        parse(source_code)

    expected_message = "Parse error: Expected ';' after statement on line 1"
    assert expected_message in str(excinfo.value), f"Expected '{expected_message}' in exception, but got '{excinfo.value}'"

    print("Missing semicolon error detected!")


def test_missing_parenthesis_parse_function_call():
    source_code_1 = """def s (int n) {
        yap(n);
    }
    s(5;
    """

    with pytest.raises(ParseError) as excinfo:
        parse(source_code_1)

    expected_message_1 = "Parse error: Expected ')' after function arguments on line 4"
    assert expected_message_1 in str(excinfo.value), f"Expected '{expected_message_1}' in exception, but got '{excinfo.value}'"

    print("Missing parenthesis error 1 detected!")

    source_code_2 = """def s (int n) {
        yap(n);
    }
    s(5
    """

    with pytest.raises(ParseError) as excinfo:
        parse(source_code_2)

    expected_message_2 = "Parse error: Unexpected end of input, expected ')' on line 4"
    assert expected_message_2 in str(excinfo.value), f"Expected '{expected_message_2}' in exception, but got '{excinfo.value}'"

    print("Missing parenthesis error 2 detected!")

    source_code_3 = """def func {
        yap("nothing");
    }
    """

    with pytest.raises(ParseError) as excinfo:
        parse(source_code_3)

    expected_message_3 = "Parse error: Expected '(' after function name on line 2"
    assert expected_message_3 in str(excinfo.value), f"Expected '{expected_message_3}' in exception, but got '{excinfo.value}'"

    print("Missing parenthesis error 3 detected!")

def test_pushing_multiple_elements_stack_parse_function_call():
    source_code = """stack<int> s1;
    s1.stackPush(5, 7);
    """

    with pytest.raises(ParseError) as excinfo:
        parse(source_code)

    expected_message = "Parse error: Stack push expects exactly 1 argument, got 2 on line 2"
    assert expected_message in str(excinfo.value), f"Expected '{expected_message}' in exception, but got '{excinfo.value}'"

    print("Pushing multiple elements in stack error detected!")

def test_pushing_multiple_elements_queue_parse_function_call():
    source_code = """queue<int> s1;
    s1.queuePush(5, 7);
    """

    with pytest.raises(ParseError) as excinfo:
        parse(source_code)

    expected_message = "Parse error: Queue push expects exactly 1 argument, got 2 on line 2"
    assert expected_message in str(excinfo.value), f"Expected '{expected_message}' in exception, but got '{excinfo.value}'"

    print("Pushing multiple elements in queue error detected!")

def test_len_arguments_parse_function_call():
    source_code = """int[] arr = [1,2,3];
    arr.len(1);
    """

    with pytest.raises(ParseError) as excinfo:
        parse(source_code)

    expected_message = "Parse error: len function takes no arguments on line 2"
    assert expected_message in str(excinfo.value), f"Expected '{expected_message}' in exception, but got '{excinfo.value}'"

    print("Passing arguments in 'len' error detected!")


