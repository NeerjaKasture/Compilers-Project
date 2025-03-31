string x = "hello";
yap(x[1]);
stack<int> st;
st.push(3);
yap(st.top());
for(int i = 0; i < 3; i = i + 1){
    st.push(i);
    yap(st.top());
}
