    iput-object First_var, p0, Class_string;->obj1:Ljava/lang/Object;
    
    iput-object Second_var, p0, Class_string;->obj2:Ljava/lang/Object;
    
    iget-object First_var, p0, Class_string;->lator:X/Lator;

    const-string Second_var, "FUN"

    invoke-virtual {First_var, Second_var}, X/Lator;->interp(Ljava/lang/String;)Ljava/lang/String;
    
    move-result-object Second_var
    
    iput-object Second_var, p0, Class_string;->dec:Ljava/lang/String;
    
    iget-object First_var, p0, Class_string;->voker:X/Voker;
    
    new-instance Second_var, Trigger_class_type;

    invoke-virtual {First_var, Second_var}, X/Voker;->UpO(Trigger_class_type;)V
    
    iget-object Second_var, p0, Class_string;->dec:Ljava/lang/String;

    invoke-virtual {First_var, Second_var}, X/Voker;->UpF(Ljava/lang/String;)V

    invoke-virtual {First_var}, X/Voker;->voN()ret_type
    
    iget-object First_var, p0, Class_string;->obj1:Ljava/lang/Object;
    
    iget-object Second_var, p0, Class_string;->obj2:Ljava/lang/Object;
    
