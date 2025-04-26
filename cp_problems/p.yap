def u(int n) -> int {
    int result = 0;
    int sign = 1;
    for (int i = 0; i <= 10; i = i + 1) {
        int term = sign * (n ^ i);
        result = result + term;
        sign = sign * ~1;
    }
    yeet result
}

def interpolate(int[] x, int[] y, int n) -> int {
    int result = 0;
    int k = x.len();
    for (int i = 0; i < k; i = i + 1) {
        int term = y[i];
        for (int j = 0; j < k; j = j + 1) {
            if (j != i) {
                term = term * (n - x[j]) / (x[i] - x[j]);
            }
        }
        result = result + term;
    }
    yeet result
}

int sum = 0;
for (int k = 1; k <= 10; k = k + 1) {
    int[] x = [];
    int[] y = [];
    for (int i = 1; i <= k; i = i + 1) {
        x.append(i);
        y.append(u(i));
    }
    int prediction = interpolate(x, y, k + 1);
    int actual = u(k + 1);
    if (prediction != actual) {
        sum = sum + prediction;
    }
}
yap(sum);