string x = "hello";
yap(x[1]);
stack<int> st;
st.stackPush(4);
st.stackPush(3);
yap(st.top());
for(int i = 0; i < 3; i = i + 1){
    st.stackPush(i);
    yap(st.top());
}
int x = 5;
yap(x);
queue<int> q;
q.queuePush(3);
q.queuePush(4);
q.queuePop();
yap(q.first());
