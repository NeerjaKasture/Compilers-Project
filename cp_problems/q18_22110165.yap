def is_prime(int num) -> bool{
    for(int i=2;i<num;i=i+1){
        if((num%i)==0){
            yeet cap
        }
    }
    yeet nocap
}

int target = 10000;
int a = 0;
int b = 1;
int c = a+b;
int largest = 0;
while(c<=target){
    a=b;
    b=c;
    c=a+b;
    if(is_prime(c) and (c > largest)){
        largest = c;
    }
}
yap(largest);