# Project Euler  -  Question 2  -  Even Fibonacci Numbers
# https://projecteuler.net/problem=2
# Answer = 4613732
 
int sum = 0;     # Variable to hold sum
int num1 = 0;   # First number
int num2 = 1;   # Second number
int temp = 0;
# While the second number is less than 4000000
# This ensures the first number is less after moving
while(num2 < 4000000){
    temp = num1;
    num1 = num2;
    num2 = num1 + temp;
 
    # If the number is eve, add to sum
    if((num1%2) == 0){
        sum = sum + num1;
    }
}
yap("The sum is: ",sum);