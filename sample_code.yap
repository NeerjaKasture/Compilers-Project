
def inc(int x) -> int {
    yeet x + 1
}

def square(int x) -> int {
    yeet x * x
}

fn[] ops = [inc, square];
yap(ops[0](5));  # Expect 6
yap(ops[1](3));  # Expect 9


# def closure_func(int x) -> fn {
#     def f(int y)->int{
#         yeet x*x
#     }

#     yeet f
# }

# fn g = closure_func(5);
# yap(g(2)); # prints 10


