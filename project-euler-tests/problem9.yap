# Project Euler  -  Question 9  -  Special Pythagorean Triplet 
# https://projecteuler.net/problem=9
# Answer = 31,875,000 

for(int a=1;a<1000;a=a+1){
    for(int b=a;b<1000;b=b+1){
        for(int c=b;c<1000;c=c+1){
            if((a+b+c)==1000){
                if((a*a + b*b) == (c*c)){
                    yap("A",a,"B",b,"C",c);
                    yap("Product", (a*b*c));
                }
            }
        }
    }
}