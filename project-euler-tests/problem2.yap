int first = 0;
int second = 1;
int sum = 0;

while(second < 4000000){
    int temp = first;
    first = second;
    second = temp + second;

    if((first%2) == 0){
        sum=sum+first;
    }
}

yap(sum);