# ANSWER = 25,164,150

int sumSquare = 0;
 
# Keep track of the the sums
int sums = 0;
 

for(int i=1;i<101;i=i+1){
    sumSquare = sumSquare + i*i;
    sums = sums+ i;
}
 
# Square the individuals sums to find square of sums
int squareSum = sums * sums;
 
yap("The sum of the squares is: " , sumSquare);
yap("The square of the sums is: " , sums);
yap("The difference is: " , (squareSum - sumSquare));