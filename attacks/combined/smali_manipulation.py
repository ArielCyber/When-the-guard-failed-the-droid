import sys
import os
import glob

#find two earlist registers to replace
def find_two_availables(var_string,sum_vars):
	if not var_string or not ("v" in var_string):#no vars in fun
		if sum_vars<2:
			return [sum_vars,sum_vars+1,"y"]
		else:
			return [sum_vars,sum_vars+1,"n"]
	else:#there are vars in the func
		if ".." in var_string:
			vars_from_string=var_string.split(" .. ")
			first=int(vars_from_string[0].strip()[-1])
			second=int(vars_from_string[1].strip()[-1])
			vs_list=range(first,second,1)
		else:
			vis=var_string.split(",")	
			vs_list=[]
		     	for v in vis:
		     		vs_list.append(int(v[-1]))
	#get the available vars in 15 vars
     	ran=range(0,sum_vars,1)
     	s = set(vs_list)
	avail_var = [x for x in ran if x not in s]
	if len(avail_var)<2:#not enought registers
		return [sum_vars,sum_vars+1,"y"]
     	first_v=avail_var[0]
     	second_v=avail_var[1]
        return [first_v,second_v,"n"]

#cound check of local var
def bound_check(locals_var,var):
        if not "p" in var:
                if int(var[1:])>15:
                        return 1
                else:
                        return 0
        p_num=int(var[1:])+locals_var
        if p_num>15:
                return 1
        return 0
                 	
#smali code manipulation for functions
def smali_manip(structure,file_list,index_of_change,end_func,letter,root,class_title,class_string,path_to_context):
	
        #create the manipuation files if needed
        #update package name to helpers
        
	helpers=os.listdir("helpers")
	helpers.remove("apkkey.keystore")
	helpers.remove("MyApplication.smali")
	for help in helpers:
		name=root+help
		if os.path.isfile(name):#allready have files in dir
		        continue
		os.system("cp "+"helpers/"+help+" "+name)
		newText=""
		with open(name,'r') as f:                   
	            	newText=f.readlines()
	        f.close()
	        for i in range(0,len(newText)):
	        	newText[i]=newText[i].replace('X/', class_title)
	        	newText[i]=newText[i].replace('Y/MyApplication', path_to_context+"MyApplication")

		with open(name, "w") as f:
			for i in newText:
				f.write(i)
		f.close()
	
        try:
                
                if not letter=="F" and ";->" not in file_list[index_of_change]:#take care of non function strings
		        	        
                	        return smali_manip_non_func(structure,file_list,index_of_change,end_func,root,class_string,letter)
                #get the data for function
                class_to_run,func_name,ret_type,arguments,args_types,locals_amount=structure
		
                class_var=arguments[1].strip().split(",")[0]
                
	        if class_var=="":#no parameter function
		        return smali_manip_no_args(structure,file_list,index_of_change,end_func,root,class_string)	     
	        if ".." in class_var:
		        class_var=class_var.split("..")[0].strip()
	        
	        #read the snippet
	        with open(root+"/clinit.smali","r") as r:
		        mals=r.readlines()
	        r.close()
	        
	        if len(ret_type)!=1:#return type update
		        ret_type="L"+ret_type.replace(".","/")+";"
	        #prologue for the changes
	        #general replacements of two registers
	        first_v,second_v,change_locals_flag=find_two_availables(arguments[1],locals_amount)
		#update the locals line if needed
		if change_locals_flag=="y":#a change is needed in the locals line
			ind=find_function_locals(file_list,index_of_change)
			amount=file_list[ind].split(" ")[-1]
			amount_int_increase=int(amount)+2
			file_list[ind]=file_list[ind].replace(amount,str(amount_int_increase))

		first_v="v"+str(first_v)
		second_v="v"+str(second_v)
	        #first range branch
	        tmp_check=bound_check(locals_amount,first_v)+bound_check(locals_amount,second_v)+bound_check(locals_amount,class_var)
	        if tmp_check>0:#too high register 
	        	mals=[m.replace('First_var, Second_var', 'First_var .. Second_var') for m in mals]
	        	mals=[m.replace('{Trigger_class}', '{Trigger_class .. Trigger_class}') for m in mals]
	        	mals=[m.replace('invoke-virtual ', 'invoke-virtual/range ') for m in mals]
	        
	        #gerenal additional replacements
	        mals[18]=mals[18].replace('Trigger_class_type', class_to_run)
	        mals=[m.replace('Class_string;', class_string) for m in mals]
	        mals[6]=mals[6].replace("FUN",func_name)
	        
	      
	        mals=[m.replace('Trigger_class', class_var) for m in mals]
	        mals=[m.replace('First_var', first_v) for m in mals]
	        mals=[m.replace('Second_var', second_v) for m in mals]
	        #update the triger class,ret type and args_types in the malware snipper
	        mals[26]=mals[26].replace("()","("+args_types+")")
	        mals[26]=mals[26].replace("ret_type",ret_type+"\n")
	        mals[26]=file_list[index_of_change].split("}")[0]+"}"+mals[26].split("}")[1]
	        
	        
	        #decide the right vo(ker) function to use
	        #1 for void func and no args
	        #2 for object func and no args
	        #3 for object func and object array args
	        #4 for void func and object array args
	        if arguments[1].split(",")>1 or arguments[1].split("..")>1:
		        if ret_type=="V":
			        mals[26]=mals[26].replace("voN","vo4")
		        else:
			        mals[26]=mals[26].replace("voN","vo3")
	        else:
		        if ret_type=="V":
			        mals[26]=mals[26].replace("voN","vo1")
		        else:
			        mals[26]=mals[26].replace("voN","vo2")
		#add the return of the answer to the register
		if ret_type!="V":
			line_flag=False
			count=1
			while True:#check the next line if it is a move result line
				if line_flag:
					break
				if not file_list[index_of_change+count].strip():#loop until real line
					count+=1
				else:
					line_flag=True
			if file_list[index_of_change+count].startswith("    move-result"):#if need to replace move-result line
				index=index_of_change+count
				mals.insert(27,file_list[index])
				
				#check if the return of the object from voker, of the env. vars is useless, erase it.
				var=file_list[index].split(" ")[-1]#get the ending var of move-result function
				del file_list[index]#delete former move-result line
				if var==class_var:#no need to return the object
					del mals[28]
					del mals[30]
				if var==first_v:
					del mals[32]
				if var==second_v:
					del mals[34]
			#check if the globals are needed
			check_f=0
			check_s=0
			start_of_func=find_function_declaration(file_list,index_of_change)
			#check if the globals are needed through the relevant lines
			for line in file_list[start_of_func:index_of_change]:
				line=line.split()
				if first_v in line:
					check_f=1
				if second_v in line:
					check_s=1
				if check_f+check_s==2:
					break
			#if they were not mentioned, no need to initilize the globs
			if check_s==0:

				try:
					if "obj2:Ljava/lang/Object;" in mals[34]:
						del mals[34]
				except:
					pass
			if check_f==0:
				
				try:
					if "obj1:Ljava/lang/Object;" in mals[32]:
						del mals[32]
				except:
					pass
			if check_s==0:
				del mals[2]
			if check_f==0:
				del mals[0]
			
				
	        #end proc
                return end_of_manip(file_list,index_of_change,mals)
        except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print exc_type,exc_obj, fname, exc_tb.tb_lineno
		print index_of_change
                return file_list
	
#smali code manipulation for non functions
def smali_manip_non_func(structure,file_list,index_of_change,end_func,root,class_string,letter):
        try:
                class_var,func_name,locals_amount=structure
                
                #read the snippet
	        with open(root+"/clinit_non_func.smali","r") as r:
		        mals=r.readlines()
	        r.close()
	        if letter=="I":#use other function for domains
	        	mals[8]=mals[8].replace("interp","interpDom")
	        #Lator class var
		mals=[m.replace('Class_string;', class_string) for m in mals]	      
	        mals[6]=mals[6].replace("FUN",func_name)
	        


		first_v,second_v,change_locals_flag=find_two_availables("",locals_amount)
		#update the locals line if needed
		if change_locals_flag=="y":#a change is needed in the locals line
			ind=find_function_locals(file_list,index_of_change)
			amount=file_list[ind].split(" ")[-1]
			amount_int_increase=int(amount)+2
			file_list[ind]=file_list[ind].replace(amount,str(amount_int_increase))

		first_v="v"+str(first_v)
		second_v="v"+str(second_v)
	      	#first range branch
	        class_var=class_var.replace("{","")
	        mals=[m.replace('First_var', first_v) for m in mals]
	        mals=[m.replace('Second_var', second_v) for m in mals]
	        mals=[m.replace('Result_var', class_var) for m in mals]
			
                #end proc
                return end_of_manip(file_list,index_of_change,mals)
        except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print exc_type,exc_obj, fname, exc_tb.tb_lineno,structure

                return file_list
                
#smali code manipulation for non functions
def smali_manip_no_args(structure,file_list,index_of_change,end_func,root,class_string):
        try:
                class_to_run,func_name,ret_type,arguments,args_types,locals_amount=structure
	        
	        
	        with open(root+"/clinit_no_args.smali","r") as r:
		        mals=r.readlines()
	        r.close()
	        #Lator class var
	
	        #prologue for the changes
	        #general replacements
	        mals=[m.replace('Trigger_class_type', class_to_run) for m in mals]
	        mals=[m.replace('Class_string;', class_string) for m in mals]
	        mals[6]=mals[6].replace("FUN",func_name)
	        

		if len(ret_type)!=1:#return type update
		        ret_type="L"+ret_type.replace(".","/")+";"
	        #prologue for the changes
	        #general replacements of two registers
	        first_v,second_v,change_locals_flag=find_two_availables(arguments[1],locals_amount)
		#update the locals line if needed
		if change_locals_flag=="y":#a change is needed in the locals line
			ind=find_function_locals(file_list,index_of_change)
			amount=file_list[ind].split(" ")[-1]
			amount_int_increase=int(amount)+2
			file_list[ind]=file_list[ind].replace(amount,str(amount_int_increase))

		first_v="v"+str(first_v)
		second_v="v"+str(second_v)
	      	#first range branch
	      	tmp_check=bound_check(locals_amount,first_v)+bound_check(locals_amount,second_v)
	        if tmp_check>0:#too high register 
	        	mals=[m.replace('First_var, Second_var', 'First_var .. Second_var') for m in mals]
	        	mals=[m.replace('{First_var}', '{First_var .. First_var}') for m in mals]
	        	mals=[m.replace('invoke-virtual ', 'invoke-virtual/range ') for m in mals]
	        mals=[m.replace('Trigger_class', class_var) for m in mals]
	        mals=[m.replace('First_var', first_v) for m in mals]
	        mals=[m.replace('Second_var', second_v) for m in mals]
	        #update the triger class,ret type and args_types in the malware snipper
	        mals[24]=mals[24].replace("ret_type",ret_type+"\n")
	        #mals[24]=file_list[index_of_change].split("}")[0]+"}"+mals[24].split("}")[1]
		if ret_type=="V":
			mals[24]=mals[24].replace("voN","vo4")
		else:
			mals[24]=mals[24].replace("voN","vo3")
		#add the return of the answer to the register
		if ret_type!="V":
			index=find_string(file_list,index_of_change,"    move-result")
			mals.insert(25,file_list[index])
			
			#check if the return of the object from voker, of the env. vars is useless, erase it.
			var=file_list[index].split(" ")[-1]#get the ending var of move-result function
			del file_list[index]#delete former move-result line
			
			if var==first_v:
				del mals[26]
			if var==second_v:
				del mals[28]
		
		
		check_f=0
		check_s=0
		start_of_func=find_function_declaration(file_list,index_of_change)
		#check if the globals are needed through the relevant lines
		for line in file_list[start_of_func:index_of_change]:
			line=line.split()
			if first_v in line:
				check_f=1
			if second_v in line:
				check_s=1
			if check_f+check_s==2:
				break
		#if they were not mentioned, no need to initilize the globs
		if check_s==0:

			try:
				if "obj2:Ljava/lang/Object;" in mals[28]:
					del mals[28]
			except:
				pass
		if check_f==0:
			
			try:
				if "obj1:Ljava/lang/Object;" in mals[26]:
					del mals[26]
			except:
				pass
		if check_s==0:
			del mals[2]
		if check_f==0:
			del mals[0]
		
                #end proc
                return end_of_manip(file_list,index_of_change,mals)
        except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print exc_type,exc_obj, fname, exc_tb.tb_lineno,structure

                return file_list
                

#end of manipulation procedure 
def end_of_manip(file_list,index_of_change,mals):

	#update mal script to code
	del file_list[index_of_change]
	file_list=file_list[:index_of_change]+mals+file_list[index_of_change:]
	return file_list

#get the first line with the phrase in the list
def find_string(list_of_strings,starter,phrase):
	for i in range(starter,len(list_of_strings)-1,1):
		if list_of_strings[i].startswith(phrase):
			return i
	return -1
#get the first line with the phrase in the list
def find_string_with_end(list_of_strings,starter,end,phrase):
	for i in range(starter,end,1):
		if phrase in list_of_strings[i]:
			return i
	return -1

#get the enclosing function
def find_function_locals(important,line_number):
	for i in range(line_number,0,-1):
		if important[i].startswith("    .locals"):
			return i
#get the enclosing function
def find_function_declaration(important,line_number):
	for i in range(line_number,0,-1):
		if important[i].startswith(".method"):
			return i
