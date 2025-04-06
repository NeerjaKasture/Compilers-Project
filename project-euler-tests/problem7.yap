# Project Euler  -  Question 7  -  10,001st prime

# ANSWER = 104,743

def is_prime(int num) -> bool{
    for(int i=2;i<num;i=i+1){
        if((num%i)==0){
            yeet cap
        }
    }
    yeet nocap
}
 
int count = 1;  # Number of primes
int num = 2 ;    # Prime number (count)
 
while (count<10001){
    num=num+1;
    if(is_prime(num)){
        count=count+1;
    }
}
yap("The 10001th prime is: " , num);