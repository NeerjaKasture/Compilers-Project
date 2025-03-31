# How to Write Code in YAP?

## 1. Variables and Data Types

The datatype of the variable must be defined by the user at the time of declaration. You can declare variables using the following types:

- `int` - Whole numbers
- `float` - Decimal numbers
- `bool` - `nocap` (true) or `cap` (false)
- `string` - Text
- `int[]`, `float[]`, `bool[]`, `string[]` - Arrays

### Declaring Variables:
```yap
int age = 25;
float pi = 3.14;
bool isStudent = nocap;
string name = "Alice";
```

## 2. Printing Output

Use `yap()` to display values.

### Example: Printing
```yap
yap("Hello, world!");
int x = 10;
yap(x);
```
**Output:**
```
Hello, world!
10
```

## 3. Taking User Input

Use `spill()` to get values from the user.

### Example: Input
```yap
int age = spill();
yap("Your age is: ", age);
```
If you enter `20`, output will be:
```
Your age is: 20
```

## 4. Operations

### 4.1 Arithmetic Operations
| Operator | Name            | Example | Output |
|----------|----------------|---------|--------|
| `+`      | Addition       | `5+3`   | `8`    |
| `-`      | Subtraction    | `5-3`   | `2`    |
| `*`      | Multiplication | `5*3`   | `15`   |
| `/`      | Division       | `6/3`   | `2.0`  |
| `^`      | Exponentiation | `5^3`   | `125`  |
| `~`      | Unary Negation | `~2`    | `-2`   |
| `%`      | Modulo         | `10%3`    | `1`   |

### 4.2 Comparison Operations
| Operator | Name                    | Example | Output |
|----------|-------------------------|---------|--------|
| `<`      | Less than                | `5<3`   | `cap`  |
| `>`      | Greater than             | `5>3`   | `nocap`|
| `<=`     | Less than or equal to    | `5<=3`  | `cap`  |
| `>=`     | Greater than or equal to | `5>=3`  | `nocap`|
| `==`     | Equal to                 | `5==3`  | `cap`  |
| `!=`     | Not equal to             | `5!=3`  | `nocap`|

### 4.3 Logical Operations
| Operator | Name  | Example        | Output |
|----------|-------|---------------|--------|
| `and`    | AND   | `nocap and cap` | `cap`  |
| `or`     | OR    | `nocap or cap`  | `nocap`|
| `not`    | NOT   | `not cap`      | `nocap`|

### 4.4 Bitwise Operations
| Operator | Name | Example | Binary Calculation | Output |
|----------|------|---------|--------------------|--------|
| `&`      | AND  | `5&3`   | `101 & 011 = 001` | `1`    |
| `\|`      | OR   | `5\|3`   | `101 \| 011 = 111` | `7`    |
| `~~`     | NOT  | `~~3`   | `~011 = 100`      | `-4`   |

## 5. Conditional Statements

Use `if`, `elif`, and `else` for decision-making.

### Example: If-Else
```yap
int num = spill();
if (num > 0) {
    yap("Positive number");
} elif (num < 0) {
    yap("Negative number");
} else {
    yap("Zero");
}
```
**Input:** `5`
**Output:**
```
Positive number
```

## 6. Loops

### 6.1 `while` loop
```yap
int count = 0;
while (count < 5) {
    yap(count);
    count = count + 1;
}
```
**Output:**
```
0
1
2
3
4
```

### 6.2 `for` loop
```yap
for (int i = 0; i < 5; i = i + 1) {
    yap(i);
}
```
**Output:**
```
0
1
2
3
4
```

### 6.3 `break` and `continue`

‘break’ and ‘continue’ are the standard loop control statements
break: Exits the loop immediately.
continue: Skips the current iteration and moves to the next one.

```yap
for (int i = 0; i < 5; i = i + 1) {
    yap(i);
    if (i==2){
     break;
    }
}
```
**Output:**
```
0
1
2
```
```yap
for (int i = 0; i < 5; i = i + 1) {
    if (i==2){
     continue;
    }
    yap(i);
}
```
**Output:**
```
0
1
3
4
```

## 7. Arrays
Arrays can be defined for any of these types: int[], float[], bool[], string[]. Arrays having elments of different datatypes are not supported.
```yap
int[] numbers = [1, 2, 3, 4];
string[] words = ["hello", "world"];
```

### Access array elements: 
```yap
yap(numbers[2]);
```
**Output:**
```
3
```
### Modify array elements:
```yap
numbers[1] = 10;
yap(numbers[1]);
```
**Output:**
```
10
```
### Appending Elements
```yap
numbers.append(5);
yap(numbers);
```
**Output:**
```
[1, 10, 3, 4, 5]
```

### Deleting Elements
Delete takes the index of the element which is to be deleted
```yap
numbers.delete(1);
yap(numbers);
```
**Output:**
```
[1, 3, 4, 5]
```
### Finding length
```yap
yap(numbers.len());
```
**Output:**
```
4
```

## 8. Functions

### Function with Parameters
```yap
def add(int a, int b) -> int {
    yeet a + b
}
yap(add(5, 3));
```
**Output:**
```
8
```

### Function without Return Value
```yap
def greet(string name) {
    yap("Hello, ", name);
}
greet("Alice");
```
**Output:**
```
Hello, Alice
```

### Recursive Function
```yap
def fib(int n) -> int{
    if((n==1) or (n==0) ){
        yeet n
    }
    int x = fib(n-1) + fib(n-2);
    yeet x
}
yap(fib(8));
```
**Output:**
```
21
```

### Functions as First-Class Values
```yap
def add(int a, int b) -> int {
    yeet a + b
}
def multiply(int x, int y) -> int {
    yeet x * y
}
yap(multiply(add(2, 3), 4));
```
**Output:**
```
20
```

