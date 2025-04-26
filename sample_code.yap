yap("test_no_17");
def double(int x) -> int {
    yeet x * 2
}

fn f = double;
yap(f(5));  # Expect 10

yap("test_no_18");
def doub(int x) -> int {
    yeet x * 2
}

def apply_twice(fn f, int x) -> int {
    yeet f(f(x))
}

yap(apply_twice(doub, 2));  # Expect 8
