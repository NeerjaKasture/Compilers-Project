hashmap < string , string > m;
m["a"] = "apple";
m["b"] = "banana";
yap(m["a"]);         
yap(m["b"]);    
yap(m.len());      
m.delete("a");
yap(m.len());   