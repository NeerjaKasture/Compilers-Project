# Project Euler  -  Question 5  -  Smallest Multiple
# https://projecteuler.net/problem=5
# Answer = 232,792,560

# ------------------------------------------------------
# Second solution --------------------------------------
# ------------------------------------------------------
 
int num = 0;
bool keepGoing = nocap;

while(keepGoing){
    num = num + 20;
 
    int numMultiples = 0;

    for(int i=20;i>10;i=i-1){
        if((num%i)!=0){
            break;
        }
        if(i==11){
            keepGoing=cap;
            break;
        }
    }
 
    # Print out current num to keep track (in millions)
    if((num % 1000000) == 0){
        yap(num/1000000);
    }
}
yap("The lowest common multiple is: ", num);