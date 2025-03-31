from parser import *

def test_variable_declarations():
    source_code = """
    int x = 5;
    float y = 2.5;
    bool z = nocap;
    string msg = "Hello";
    """
    
    expected_output = Sequence([
        Declaration(type='int', name='x', value=Number(val='5')),
        Declaration(type='float', name='y', value=Number(val='2.5')),
        Declaration(type='bool', name='z', value=Boolean(val='nocap')),
        Declaration(type='string', name='msg', value=String(val='Hello'))
    ])
    
    assert parse(source_code).statements == expected_output.statements
    print("Variable declarations test passed!")

def test_conditional_statements():
    source_code = """
    int num = spill();
    if (num > 0) {
        yap("Positive number");
    } elif (num < 0) {
        yap("Negative number");
    } else {
        yap("Zero");
    }
    """

    expected_output = Sequence([
        Declaration(type='int', name='num', value=Input(type='int')),
        Cond(
            If=(BinOp(op='>', left=Variable(val='num'), right=Number(val='0')),
                Sequence([Print(values=[String(val="Positive number")])])
            ),
            Elif=[
                (BinOp(op='<', left=Variable(val='num'), right=Number(val='0')),
                 Sequence([Print(values=[String(val="Negative number")])]))
            ],
            Else=Sequence([Print(values=[String(val="Zero")])])
        )
    ])
    
    assert parse(source_code).statements == expected_output.statements
    print("Conditional statements test passed!")

def test_for_loop():
    source_code = """
    for (int i = 0; i < 5; i = i + 1) {
        yap("Iteration:", i);
    }
    """

    expected_output = Sequence([
        For(
            init=Declaration(type='int', name='i', value=Number(val='0')),
            condition=BinOp(op='<', left=Variable(val='i'), right=Number(val='5')),
            increment=Assignment(name='i', value=BinOp(op='+', left=Variable(val='i'), right=Number(val='1'))),
            body=Sequence([Print(values=[String(val='Iteration:'), Variable(val='i')])])
        )
    ])
    
    assert parse(source_code).statements == expected_output.statements
    print("For loop test passed!")

def test_nested_while_loops():
    source_code = """
    int outer = 1;
    while (outer < 3) {
        int inner = 1;
        while (inner < 3) {
            yap("outer:", outer, " inner:", inner);
            inner = inner + 1;
        }
        outer = outer + 1;
    }
    """
    
    expected_output = Sequence([
        Declaration(type='int', name='outer', value=Number(val='1')),
        While(
            condition=BinOp(op='<', left=Variable(val='outer'), right=Number(val='3')),
            body=Sequence([
                Declaration(type='int', name='inner', value=Number(val='1')),
                While(
                    condition=BinOp(op='<', left=Variable(val='inner'), right=Number(val='3')),
                    body=Sequence([
                        Print(values=[String(val='outer:'), Variable(val='outer'), String(val=' inner:'), Variable(val='inner')]),
                        Assignment(name='inner', value=BinOp(op='+', left=Variable(val='inner'), right=Number(val='1')))
                    ])
                ),
                Assignment(name='outer', value=BinOp(op='+', left=Variable(val='outer'), right=Number(val='1')))
            ])
        )
    ])
    
    assert parse(source_code).statements == expected_output.statements
    print("Nested while loops test passed!")

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

    expected_output = Sequence([Declaration(type='int[]', name='numbers', value=Array(elements=[Number(val='1'), Number(val='2'), Number(val='3'), Number(val='4'), Number(val='5')])), Print(values=[String(val='Original array:'), Variable(val='numbers')]), Print(values=[String(val='Sum of all elements: '), BinOp(op='+', left=BinOp(op='+', left=BinOp(op='+', left=BinOp(op='+', left=ArrayAccess(array=Variable(val='numbers'), index=Number(val='0')), right=ArrayAccess(array=Variable(val='numbers'), index=Number(val='1'))), right=ArrayAccess(array=Variable(val='numbers'), index=Number(val='2'))), right=ArrayAccess(array=Variable(val='numbers'), index=Number(val='3'))), right=ArrayAccess(array=Variable(val='numbers'), index=Number(val='4')))]), Print(values=[String(val='First element:'), ArrayAccess(array=Variable(val='numbers'), index=Number(val='0'))]), ArrayAssignment(array=Variable(val='numbers'), index=Number(val='2'), value=Number(val='10')), Print(values=[String(val='Modified array:'), Variable(val='numbers')]), ArrayAppend(array=Variable(val='numbers'), value=Number(val='6')), Print(values=[String(val='After append:'), Variable(val='numbers')]), ArrayDelete(array=Variable(val='numbers'), index=Number(val='0')), Print(values=[String(val='After delete:'), Variable(val='numbers')]), Declaration(type='string[]', name='words', value=Array(elements=[String(val='Hello'), String(val='World')])), Print(values=[String(val='String array:'), Variable(val='words')]), ArrayAssignment(array=Variable(val='words'), index=Number(val='0'), value=String(val='hi')), Print(values=[String(val='Modified string array:'), Variable(val='words')])])

    assert parse(source_code).statements == expected_output.statements
    print("Arrays test passed!")

def test_functions_1():
    source_code = """
    # Function that generates an array of multiples of 3
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
    yap(generateArray(5));  # Expected Output: [0, 3, 6, 9, 12]
    """

    expected_output = Sequence([Function(name='generateArray', params=[('int', 'n')], return_type='int[]', body=Sequence([Cond(If=(BinOp(op='<=', left=Variable(val='n'), right=Number(val='0')), Sequence([Return(value=Array(elements=[]))])), Elif=[], Else=None), Declaration(type='int[]', name='arr', value=Array(elements=[])), For(init=Declaration(type='int', name='i', value=Number(val='0')), condition=BinOp(op='<', left=Variable(val='i'), right=Variable(val='n')), increment=Assignment(name='i', value=BinOp(op='+', left=Variable(val='i'), right=Number(val='1'))), body=Sequence([ArrayAppend(array=Variable(val='arr'), value=BinOp(op='*', left=Variable(val='i'), right=Number(val='3')))])), Return(value=Variable(val='arr'))])), Print(values=[FunctionCall(name='generateArray', params=[Number(val='5')])])])

    assert parse(source_code).statements == expected_output.statements
    print("Functions test 1 passed!")

def test_functions_2():
    source_code = """
    def add(int a, int b) -> int {
        yeet a + b
    }
    def multiply(int x, int y) -> int {
        yeet x * y
    }
    yap(multiply(add(2, 3), 4)); 
    """

    expected_output = Sequence([Function(name='add', params=[('int', 'a'), ('int', 'b')], return_type='int', body=Sequence([Return(value=BinOp(op='+', left=Variable(val='a'), right=Variable(val='b')))])), Function(name='multiply', params=[('int', 'x'), ('int', 'y')], return_type='int', body=Sequence([Return(value=BinOp(op='*', left=Variable(val='x'), right=Variable(val='y')))])), Print(values=[FunctionCall(name='multiply', params=[FunctionCall(name='add', params=[Number(val='2'), Number(val='3')]), Number(val='4')])])])

    assert parse(source_code).statements == expected_output.statements
    print("Functions test 2 passed!")

def test_functions_3():
    source_code = """
    def fib(int n) -> int{
        if((n==1) or (n==0) ){
            yeet n
        }
        
        int x = fib(n-1) + fib(n-2);
        yeet x
    }

    yap(fib(8));
    """

    expected_output = Sequence([Function(name='fib', params=[('int', 'n')], return_type='int', body=Sequence([Cond(If=(BinOp(op='or', left=Parenthesis(expr=BinOp(op='==', left=Variable(val='n'), right=Number(val='1'))), right=Parenthesis(expr=BinOp(op='==', left=Variable(val='n'), right=Number(val='0')))), Sequence([Return(value=Variable(val='n'))])), Elif=[], Else=None), Declaration(type='int', name='x', value=BinOp(op='+', left=FunctionCall(name='fib', params=[BinOp(op='-', left=Variable(val='n'), right=Number(val='1'))]), right=FunctionCall(name='fib', params=[BinOp(op='-', left=Variable(val='n'), right=Number(val='2'))]))), Return(value=Variable(val='x'))])), Print(values=[FunctionCall(name='fib', params=[Number(val='8')])])])

    assert parse(source_code).statements == expected_output.statements
    print("Functions test 3 passed!")

def bitwise_ops():
    source_code = """
    yap(5&3);
    yap(5|3);
    yap(~~3);
    """

    expected_output = Sequence([Print(values=[BinOp(op='&', left=Number(val='5'), right=Number(val='3'))]), Print(values=[BinOp(op='|', left=Number(val='5'), right=Number(val='3'))]), Print(values=[BinOp(op='~~', left=None, right=Number(val='3'))])])

    assert parse(source_code).statements == expected_output.statements
    print("Bitwise operations test passed!")

def test_parser():
    test_variable_declarations()
    test_conditional_statements()
    test_for_loop()
    test_nested_while_loops()
    test_arrays()
    test_functions_1()
    test_functions_2()
    test_functions_3()
    bitwise_ops()
    
    print("All tests passed!")

if __name__ == "__main__":
    test_parser()