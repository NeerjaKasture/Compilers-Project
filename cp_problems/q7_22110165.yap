def f(string input) -> int {
    int num = 0;
    for(int i=0;i<input.len();i=i+1){
        if((input[i] == "a") or (input[i] == "e") or (input[i] == "i") or (input[i] == "o") or (input[i] == "u"))
        {    num=num+1;}
    }
    yeet num 
}

# input from terminal
# int n = spill();
# int[] arr = [];
# for(int i = 0;i<n;i=i+1){
#     string input = spill();
#     int x = f(input);
#     arr.append(x);
# }

# for(int i = 0;i<n;i=i+1){
#     yap(arr[i]);
#}

string input = "aaaaaaaaaaaaaaaaaaaaaabbaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa";
yap(input.len());
yap(f(input));