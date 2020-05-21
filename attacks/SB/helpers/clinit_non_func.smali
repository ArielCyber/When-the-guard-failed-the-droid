    iput-object First_var, p0, Class_string;->obj1:Ljava/lang/Object;
    
    iput-object Second_var, p0, Class_string;->obj2:Ljava/lang/Object;
    
    iget-object First_var, p0, Class_string;->lator:X/Lator;

    const-string Second_var, "FUN"

    invoke-virtual {First_var, Second_var}, X/Lator;->interp(Ljava/lang/String;)Ljava/lang/String;
    
    move-result-object Result_var
    
    iget-object First_var, p0, Class_string;->obj1:Ljava/lang/Object;
    
    iget-object Second_var, p0, Class_string;->obj2:Ljava/lang/Object;
