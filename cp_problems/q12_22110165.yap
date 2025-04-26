int[] arr = [1,2,3,4,5];
int target = 3;

def subset_sum(int[] arr, int target){
   
    int n = arr.len();
    int[][] mat = [];
    for(int i = 0;i<n;i=i+1){
        int[] x = [];
        for(int j = 0;j<target+1;j=j+1){
            x.append(0);
        }
        mat.append(x);

    }

    for(int i = 0;i<n;i=i+1){
        mat[i][0]=1;
    }

    for(int j=0;j<target+1;j=j+1){
        if(arr[0]==j){
            mat[0][j]=1;
        }
    }
    
    for(int i =1;i<n;i=i+1){
        for(int j=1;j<target+1;j=j+1){
            if((j>=arr[i]) and (mat[(i-1)][(j-arr[i])] == 1)){
                mat[i][j] = mat[(i - 1)][(j - arr[i])];
            }
            else{
                mat[i][j] = mat[(i - 1)][j];
            }
        }
    }

    if(mat[(n-1)][target] == 1){
        int i = n-1;
        int j = target;
        while((i>0) and (j>0)){
            if(mat[i][j]!=mat[(i-1)][j]){
                yap(arr[i]);
                j=j-arr[i];
            }
            i=i-1;
        }
        if(j!=0){
            yap(arr[0]);
        }
    }
    else{
        yap("No");
    } 

}

subset_sum(arr,target);