import pytest
import sys
import os
import io
from contextlib import redirect_stdout
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from evaluator import e
from parser import parse

def test_variables():
    source_code = """
    int x = 5;
    float y = 2.5;
    bool z = nocap;
    string msg = "Hello";
    yap(x);
    yap(y);
    yap(z);
    yap(msg);
    """
    expected_output = "5\n2.5\nnocap\nHello\n"  

    ast = parse(source_code)
    f = io.StringIO()
    with redirect_stdout(f):
        e(ast)
    actual_output = f.getvalue()

    assert actual_output == expected_output, f"Expected '{expected_output}', but got '{actual_output}'"
    print("Variable declarations test passed!")

# def test_input(monkeypatch):
#     # Simulating user input
#     inputs = iter(["10", "Hello"])
#     monkeypatch.setattr('builtins.input', lambda _: next(inputs))

#     source_code = """
#     string msg = input();
#     int num = input();
#     yap(msg);
#     yap(num);
#     """
#     expected_output = "Hello\n10\n"

#     ast = parse(source_code)
#     f = io.StringIO()
#     with redirect_stdout(f):
#         e(ast)
#     actual_output = f.getvalue()
    
#     assert actual_output == expected_output, f"Expected '{expected_output}', but got '{actual_output}'"
#     print("Taking Input test passed!")

def test_conditionals():
    source_code = """
    int a = 40;
    int b = 100;
    int c = 500;
    int num = ~5;
    if (num > 0) {
        yap("Positive number");
    } elif (num < 0) {
        yap("Negative number");
    } else {
        yap("Zero");
    }
    if (a > b) {
        if (b > c) {
            yap("a > b > c");
        } else {
            if (a > c) {
                yap("a > c > b");
            } else {
                yap("c > a > b");
            }
        }
    } else {
        if (a > c) {
            yap("b > a > c");
        } else {
            if (b > c) {
                yap("b > c > a");
            } else {
                yap("c > b > a");
            }
        }
    }
    """
    expected_output = "Negative number\nc > b > a\n"  

    ast = parse(source_code)
    f = io.StringIO()
    with redirect_stdout(f):
        e(ast)
    actual_output = f.getvalue()

    assert actual_output == expected_output, f"Expected '{expected_output}', but got '{actual_output}'"
    print("Conditional statements test passed!")

def test_operations():
    source_code = """
    int a = 15;
    int b = 10;
    yap(a+b);
    yap(a-b);
    yap(a*b);
    yap(a/b);
    yap(~a);
    yap(a^2);
    yap(a%b);
    yap(a>b);
    yap(a<b);
    yap(a>=b);
    yap(a<=b);
    yap(a==b);
    yap(a!=b);
    yap(a&b);
    yap(a|b);
    yap(~~a);
    yap(nocap and cap);
    yap(nocap or cap);
    yap(not cap);
    yap("yap" == "print");
    """
    expected_output = "25\n5\n150\n1.5\n~15\n225\n5\nnocap\ncap\nnocap\ncap\ncap\nnocap\n10\n15\n~16\ncap\nnocap\nnocap\ncap\n"

    ast = parse(source_code)
    f = io.StringIO()
    with redirect_stdout(f):
        e(ast)
    actual_output = f.getvalue()

    assert actual_output == expected_output, f"Expected '{expected_output}', but got '{actual_output}'"
    print("Operations test passed!")

def test_for_loop():
    source_code = """
    for (int i = 0; i < 5; i = i + 1) {
        yap("Iteration:", i);
        if (i == 2) {
            break;
        } else {
            continue;
        }
    }
    """
    expected_output = "Iteration:0\nIteration:1\nIteration:2\n"

    ast = parse(source_code)
    f = io.StringIO()
    with redirect_stdout(f):
        e(ast)
    actual_output = f.getvalue()

    assert actual_output == expected_output, f"Expected '{expected_output}', but got '{actual_output}'"
    print("For Loops test passed!")

def test_while_loop():
    source_code = """
    int outer = 1;
    while (outer < 3) {
        int inner = 1;
        while (inner < 3) {
            if (inner == 2) {
                inner = inner + 1;
                continue;
            }
            yap("outer:", outer, " inner:", inner);
            inner = inner + 1;
        }
        if (outer == 2) {
            break;
        }
        outer = outer + 1;
    }
    """
    expected_output = "outer:1 inner:1\nouter:2 inner:1\n"

    ast = parse(source_code)
    f = io.StringIO()
    with redirect_stdout(f):
        e(ast)
    actual_output = f.getvalue()

    assert actual_output == expected_output, f"Expected '{expected_output}', but got '{actual_output}'"
    print("While Loops test passed!")

def test_while_loop_2():
    source_code = """
    int count = 0;
    while (nocap) {
        if (count < 5) {
            yap("hi");
        } else {
            break;
        }
        count = count + 1;
    }
    """
    expected_output = "hi\nhi\nhi\nhi\nhi\n"

    ast = parse(source_code)
    f = io.StringIO()
    with redirect_stdout(f):
        e(ast)
    actual_output = f.getvalue()

    assert actual_output == expected_output, f"Expected '{expected_output}', but got '{actual_output}'"
    print("While Loops test passed!")

def test_arrays():
    source_code = """
    int[] numbers = [1, 2, 3, 4, 5];
    yap("Original array:", numbers);
    yap("Sum of all elements: ", numbers[0]+numbers[1]+numbers[2]+numbers[3]+numbers[4]);
    yap("First element:", numbers[0]);
    numbers[2] = 10;
    yap("Modified array:", numbers);
    numbers.append(6);
    yap("After append:", numbers);
    numbers.delete(0);
    yap("After delete:", numbers);
    string[] words = ["Hello", "World"];
    yap("String array:", words);
    words[0] = "hi";
    yap("Modified string array:", words);
    """
    expected_output = "Original array:[1, 2, 3, 4, 5]\nSum of all elements: 15\nFirst element:1\nModified array:[1, 2, 10, 4, 5]\nAfter append:[1, 2, 10, 4, 5, 6]\nAfter delete:[2, 10, 4, 5, 6]\nString array:['Hello', 'World']\nModified string array:['hi', 'World']\n"

    ast = parse(source_code)
    f = io.StringIO()
    with redirect_stdout(f):
        e(ast)
    actual_output = f.getvalue()

    assert actual_output == expected_output, f"Expected '{expected_output}', but got '{actual_output}'"
    print("Arrays test passed!")

def test_functions():
    source_code = """
    def generateArray(int n) -> int[] {
        if (n <= 0) {
            yeet []
        }
        int[] arr = [];
        for (int i = 0; i < n; i = i + 1) {
            arr.append(i * 3);
        }
        yeet arr
    }
    yap(generateArray(5));

    def add(int a, int b) -> int {
        yeet a + b
    }
    def multiply(int x, int y) -> int {
        yeet x * y
    }
    yap(multiply(add(2, 3), 4)); 

    def fib(int n) -> int{
        if((n==1) or (n==0) ){
            yeet n
        }
        
        int x = fib(n-1) + fib(n-2);
        yeet x
    }
    yap(fib(8));

    def doubleArray(int [] arr) -> int [] {
        for (int i = 0; i < 3; i = i + 1) {
            arr[i] = arr[i] * 2;
        }
        yeet arr
    }
    int[] a = [1, 2, 3];
    yap(doubleArray(a));
    """
    expected_output = "[0, 3, 6, 9, 12]\n20\n21\n[2, 4, 6]\n"

    ast = parse(source_code)
    f = io.StringIO()
    with redirect_stdout(f):
        e(ast)
    actual_output = f.getvalue()

    assert actual_output == expected_output, f"Expected '{expected_output}', but got '{actual_output}'"
    print("Functions test passed!")

def test_stack():
    source_code = """
    stack<int> s1;
    s1.stackPush(5);
    yap(s1.top());
    s1.stackPop();
    s1.stackPush(10);
    s1.stackPush(20);
    yap(s1.top());
    """
    expected_output = "5\n20\n"  

    ast = parse(source_code)
    f = io.StringIO()
    with redirect_stdout(f):
        e(ast)
    actual_output = f.getvalue()

    print("expected", expected_output)
    print("actual", actual_output)

    assert actual_output == expected_output, f"Expected '{expected_output}', but got '{actual_output}'"
    print("Stack test passed!")

def test_queue():
    source_code = """
    queue<int> q1;
    q1.queuePush(1);
    q1.queuePush(2);
    q1.queuePush(3);
    yap(q1.first()); 
    q1.queuePop();
    yap(q1.first());
    """
    expected_output = "1\n2\n"  

    ast = parse(source_code)
    f = io.StringIO()
    with redirect_stdout(f):
        e(ast)
    actual_output = f.getvalue()

    print("expected", expected_output)
    print("actual", actual_output)

    assert actual_output == expected_output, f"Expected '{expected_output}', but got '{actual_output}'"
    print("Queue test passed!")
