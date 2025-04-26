hashmap < int , int > flags;
flags[1] = 0;
flags[~2] = ~2;
yap(flags[1]);         
yap(flags[~2]);        
yap(flags.len());     
