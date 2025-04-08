yap("===== Variable Tests =====");
int x = 5;
float y = 2.5;
bool z = nocap;
string msg = "Hello";
yap(x);
yap(y);
yap(z);
yap(msg);

float t = 0.0;
t = spill();
yap(t);

yap("=====If-else test cases=====");

yap("test_no_1");
int num = spill();
if (num > 0) {
    yap("Positive number");
} elif (num < 0) {
    yap("Negative number");
} else {
    yap("Zero");
}

yap("test_no_2");
if (x > 5) { 
    yap("Greater"); 
} elif (x == 5) { 
    yap("Equal"); 
} else { 
    yap("Less"); 
}

yap("test_no_3");
if (y > 2.5 and z == nocap) { 
    yap("Complex condition true"); 
} else { 
    yap("Complex condition false"); 
}

yap("test_no_4");
if (msg == "Hello") {
    yap("String match");
    x = x + 1;
} elif (msg == "Hi") {
    yap("Hi there");
    y = y + 1.0;
} else {
    yap("No match");
    z = cap;
}

yap("test_no_5");
if ((x > 0) and (y < 5.0) or (z == nocap)) {
    yap("Multiple conditions met");
    yap(x);
    yap(y);
    yap(z);
}

yap("test_no_6");
if (num != 10) {
    x = x + 1;
    yap("Updated x:", x);
} else {
    x = x - 1;
    yap("Decreased x:", x);
}

yap("===== Nested If-Else Tests =====");
int a = 40;
int b = 100;
int c = 500;

yap("test_no_1");
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

yap("test_no_2");
if (x > 0) {
    if ((y > 2.0) and (z == nocap)) {
        yap("Complex nested condition 1");
        if (msg == "Hello") {
            yap("Deepest nesting");
        } else {
            yap("Deep nest else");
        }
    } else {
        yap("Complex nested condition 2");
    }
} else {
    yap("Outer else");
}

yap("===== For Loop Tests =====");

yap("test_no_1");
# Basic for loop
for (int i = 0; i < 5; i = i + 1) {
    yap("Iteration:", i);
}

yap("test_no_2");
for (int j = 10; (j > 0) and (x < 10); j = j - 2) {
    yap("Count down:", j);
    x = x + 1;
}

yap("test_no_3");
for (int i = 1; i < 3; i = i + 1) {
    for (int j = 1; j < 3; j = j + 1) {
        yap("i:", i, " j:", j);
    }
}

yap("===== While Loop Tests =====");
int count = 0;

yap("test_no_1");
while (count < 5) {
    yap("Count is:", count);
    count = count + 1;
}

yap("test_no_2");
while (x < 12) {
    yap("x:", x, " y:", y);
    x = x + 1;
    y = y - 0.5;
}

yap("test_no_3");
int outer = 1;
while (outer < 3) {
    int inner = 1;
    while (inner < 3) {
        yap("outer:", outer, " inner:", inner);
        inner = inner + 1;
    }
    outer = outer + 1;
}
yap("test_no_4");
int count=0;
while (count < 10) {
    yap("Count is:", count);
    if(count==3){
        break;
    }
    count = count + 1;
}
yap("test_no_5");
int count=0;
###########################infinite loop
while (count < 10) {
    yap("Count is:", count);
    if(count==3){
      # continue;   
    }
    count = count + 1;
}
yap("===== Array Tests =====");

yap("test_no_1");
int[] numbers = [1, 2, 3, 4, 5];
yap("Original array:", numbers);
yap("Sum of all elements: ", numbers[0]+numbers[1]+numbers[2]+numbers[3]+numbers[4]);

yap("test_no_2");
yap("First element:", numbers[0]);
numbers[2] = 10;
yap("Modified array:", numbers);

yap("test_no_3");
for (int i = 0; i < 5; i = i + 1) {
    numbers[i] = numbers[i] * 2;
}
yap("Doubled array:", numbers);

yap("test_no_4");
numbers.append(6);
yap("After append:", numbers);
numbers.delete(0);
yap("After delete:", numbers);

yap("test_no_5");
string[] words = ["Hello", "World"];
yap("String array:", words);
words[0] = "hi";
yap("Modified string array:", words);

yap("test_no_6");
int[] complexArray = [3, 6, 9, 12];
if (complexArray[0] < complexArray[1]) {
    if (complexArray[1] < complexArray[2]) {
        if (complexArray[2] < complexArray[3]) {
            yap("Fully ordered array");
        }
    }
}

yap("===== Function Tests =====");

yap("test_no_1");
# Function that returns the square of a number
def square(int n) -> int {
    yeet n * n
}
yap(square(4));  # Expected Output: 16

yap("test_no_2");
# Function to check if a number is even (without using %)
def isEven(int n) -> int {
    if ((n / 2) * 2 == n) {
        yeet 1
    }
    yeet 0
}
yap(isEven(10));  # Expected Output: 1
yap(isEven(7));   # Expected Output: 0

yap("test_no_3");
# Function that returns an array of numbers
def getArray(int n) -> int[] {
    yeet [1, 2, 3, 4, 5]
}
yap(getArray(5));  # Expected Output: [1, 2, 3, 4, 5]

yap("test_no_4");
# Function that returns an empty array
def emptyArray() -> int[] {
    yeet []
}
yap(emptyArray());  # Expected Output: []

yap("test_no_5");
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

yap("test_no_6");
# Function that doubles each element in the array
def doubleArray(int [] arr) -> int [] {
    for (int i = 0; i < 3; i = i + 1) {
        arr[i] = arr[i] * 2;
    }
    yeet arr
}
int[] a = [1, 2, 3];
yap(doubleArray(a));  # Expected Output: [2, 4, 6]

yap("test_no_7");
def modifyArray(int [] arr) {
    arr[1] = 100;
}
int[] arrTest = [10, 20, 30];
modifyArray(arrTest);
yap(arrTest);  # Expected Output: [10, 100, 30]

yap("test_no_8");
def increment(int n) -> int {
    yeet n + 1
}
yap(increment(square(3)));  # Expected Output: 10

yap("test_no_9");
def createArray(int n) -> int[] {
    int[] res = [];
    for (int i = 0; i < n; i = i + 1) {
        res.append(i);
    }
    yeet res
}
int[] newArr = createArray(4);
for (int i = 0; i < 4; i = i + 1) {
    yap("Element:", newArr[i]);  # Expected Output: 0, 1, 2, 3
}

yap("test_no_10");
def add(int a, int b) -> int {
    yeet a + b
}
def multiply(int x, int y) -> int {
    yeet x * y
}
yap(multiply(add(2, 3), 4)); 

yap("test_no_11");
def multiply(int x, int y) -> int {
    yeet x * y
}

def square(int x) -> int {
    yeet multiply(x, x)
}

yap(square(5)); 

yap("test_no_12");
def changeVar(int x) -> int {
    x = x + 10;
    yeet x
}
int x = 5;
yap(changeVar(x));  # Expected: 15
yap(x); 

yap("test_no_13");
def check(int x)-> int{
    for(int i=x;i<10;i=i+1){
        yap(i);
        if(i==5){
            yeet 55
        }
      
    }
    yeet 0
}
yap(check(2));

yap("test_no_14");
def check(int x) -> string {
    if (x > 0) {
        yeet "Positive"
    }
    yeet "Non-positive"
}
yap(check(5));   
yap(check(~2));

yap("test_no_15");

def fib(int n) -> int{
    if((n==1) or (n==0) ){
        yeet n
    }
    
    int x = fib(n-1) + fib(n-2);
    yeet x
}

yap(fib(8));

yap("test_no_16");
def f(int x)->int{
    def g(int y)->int{
        yeet y+1
    }
    yeet g(x)
}

yap(f(1));

yap("test_no_17");
def double(int x) -> int {
    yeet x * 2
}

fn f = double;
yap(f(5));  # Expect 10

yap("test_no_18");
def double(int x) -> int {
    yeet x * 2
}

def apply_twice(fn f, int x) -> int {
    yeet f(f(x))
}

yap(apply_twice(double, 2));  # Expect 8

yap("test_no_19");
def return_fn() -> fn {
    def say_hello() -> int {
        yap("hi");
        yeet 0
    }

    yeet say_hello
}

fn greeter = return_fn();
greeter();  # Expect: hi

yap("===== Bitwise &, |, ~~ =====");

yap(5&3);
yap(5|3);
yap(~~3);

yap("========== stack test cases ===========");
 stack<int> s1;
 s1.stackPush(5);
 yap(s1.top());
 s1.stackPop();
 s1.stackPush(10);
 s1.stackPush(20);
 yap(s1.top()); 
 
 stack<string> s2;
 s2.stackPush("hello");
 s2.stackPush("world");
 yap(s2.top()); 
 s2.stackPop();
 yap(s2.top());
 
 stack<int> s3;
 for(int i = 0; i < 5; i = i + 1) {
     s3.stackPush(i);
 }
 for(int i = 0; i < 5; i = i + 1) {
     yap(s3.top());  
     s3.stackPop();
 }
 
 yap("======== Queue test cases =========");
 queue<int> q1;
 q1.queuePush(1);
 q1.queuePush(2);
 q1.queuePush(3);
 yap(q1.first()); 
 q1.queuePop();
 yap(q1.first());
 
 queue<int> q2;
 int x = spill();  
 q2.queuePush(x);
 yap(q2.first());