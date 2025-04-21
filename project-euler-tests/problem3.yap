def is_prime(int num) -> bool{
    for(int i=2;i<num;i=i+1){
        if((num%i)==0){
            yeet cap
        }
    }
    yeet nocap
}

int[] factors = [600851475143];

while(nocap){
    if(is_prime(factors[0])){
        break;
    }
    for(int i =2; i<factors[0];i=i+1){
        if((factors[0]%i)==0){
            factors[0]=factors[0]//i;
            factors.append(i);
            break;
        }
    }
}

for(int i = 0; i<factors.len();i=i+1){
    for(int j=i;j<factors.len();j=j+1){
        if(factors[j]>factors[i]){
            int t = factors[i];
            factors[i]=factors[j];
            factors[j]=t;
        }
    }
}

yap(factors[0]);