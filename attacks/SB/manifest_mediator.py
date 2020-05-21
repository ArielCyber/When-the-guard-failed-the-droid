from bs4 import BeautifulSoup
import base64
import random
import string
import json
from smali_manipulation import *
package_name=""
import re
import socket, struct
#find the end of a function
def find_end(lines,index):
	for i in range(index,len(lines),1):
		if ".end method" in lines[i]:
			return i
			
#check lines with suspicous api
def check_lines(f,sus_api,root_package,letter,path_to_context):	
        try:
        	
	        global package_name
	        package_name=root_package
	        data_from_file=[]
	        #upper bound for change
	        with open(f,"r") as fi:
		        data_from_file=fi.readlines()
	        fi.close()
	        
	        #check if the file was inserted with the fields and clinic function
	        class_string=data_from_file[0].split()[-1]
		class_title="/".join(class_string.split("/")[:-1])+"/"
		if class_title=='/':#smali folder classes
                        class_title="L"
	        root="/".join(f.split("/")[:-1])+"/"
	        
	        for l in data_from_file:
	        	if l.startswith(".field static final"):
		        	continue
		        if sus_api.lower() in l.lower():
		        	data_from_file=update_clinit(data_from_file,class_title,class_string)#update clinit
		        	try:
					ind=data_from_file.index(l)#get the index of the suspicous line
				except:
					break#no more line like that one
			        end=find_end(data_from_file,ind)#get the end of function
			        info_structure=change_line(data_from_file,l,ind,letter)#get the info about the line
			        data_from_file=smali_manip(info_structure,data_from_file,ind,end,letter,root,class_title,class_string,path_to_context)#get the data after change
				
			                
	        with open(f,"w") as w:#write all the changes to the file
		        for i in data_from_file:
			        w.write(i)
	        w.close()
        except Exception as e:
                
	        exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		print f,sus_api
                print exc_type, exc_obj,fname, exc_tb.tb_lineno
                return

#update clinit if needed
def update_clinit(data_from_file,class_title,class_string):
	check=check_clinit(data_from_file)
	if check=="b":#bug, interface etc.
		return data_from_file
        if not check:#insert the lator and voker data to file
		#find the start of the functions
		end_of_env=find_first_method(data_from_file)
        	#stats=[".field public static lator:X/Lator;\n",".field public static voker:X/Voker;\n"]
		insts=[".field public static lator:X/Lator;\n",".field public static voker:X/Voker;\n",".field public dec:Ljava/lang/String;\n",".field public obj1:Ljava/lang/Object;\n",".field public obj2:Ljava/lang/Object;\n"]
        	clinit=[".method private constructor <init>()V\n","    .locals 1\n","    new-instance v0, X/Voker;\n" 
,"    invoke-direct {v0}, X/Voker;-><init>()V\n","    iput-object v0, p0, Class_string;->voker:X/Voker;\n","    new-instance v0, X/Lator;\n","    invoke-direct {v0}, X/Lator;-><init>()V\n","    iput-object v0, p0, Class_string;->lator:X/Lator;\n","    return-void\n",".end method\n"]
		#stats = [s.replace('X/', class_title) for s in stats]
		insts = [s.replace('X/', class_title) for s in insts]
		clinit = [s.replace('X/', class_title) for s in clinit]
		clinit = [s.replace('Class_string;', class_string) for s in clinit]

		'''ind_stats=find_string_with_end(data_from_file,0,end_of_env,"# static fields")
		
		if ind_stats==-1:#no static fields
			ind_stats=end_of_env
			data_from_file.insert(ind_stats,"# static fields\n")
			
		for st in stats:
			data_from_file.insert(ind_stats+1,st)'''
		
		ind_insts=find_string_with_end(data_from_file,0,end_of_env,"# instance fields")

		if ind_insts==-1:#add before method
			ind_insts=end_of_env
			data_from_file.insert(ind_insts,"# instance fields\n")
		for ins in insts:
			data_from_file.insert(ind_insts+1,ins)
		#check if clinit exists
		check_for_clinit_exist=find_string(data_from_file,0,"constructor <init>")
		if check_for_clinit_exist!=-1:
			end_clinit=find_string(data_from_file,check_for_clinit_exist,"    return-void")
			data_from_file=data_from_file[:end_clinit]+clinit[2:-2]+data_from_file[end_clinit:]
		else:
			for i in clinit:#append to the end the clinit func
				data_from_file.append(i)
	return data_from_file
#find if lator/voker where inserted
def check_clinit(important):
	first=find_first_method(important)
	if not first:
		return "b"#bug, interface etc.
	line_to_find=".field public static lator"	
	for i in range(0,find_first_method(important),1):
		if important[i].startswith(line_to_find):
			return True
	return False

#get the enclosing function
def find_first_method(important):
	for i in range(0,len(important),1):
			if important[i].startswith(".method"):
				return i
	return False

#get the enclosing function
def find_function_name(important,line_number):
	for i in range(line_number,0,-1):
		if important[i].startswith("    .locals"):
			return i
			

#get the enclosing catch
def find_function_catch(important,line_number):
	for i in range(line_number,len(important),1):
		line=important[i]
		l=line.strip()
		if ".catchall" in l:
			return True
		if ".catch" in l:
			return change_catch(l,i)
			
#change catch to new one
def change_catch(line,index):
	line=line.split(";")[-1]
	line="    .catchall "+line+"\n"
	return [index,line]
#analyze line from the data
def analyze_line(line,letter):
        if letter=="F" or ";->" in line:
                letter="F"
	        parameters=line.split("}")[0].split("{")
	        params_types=line.split("(")[1].split(")")[0]
	        line=line.strip("\n").split()
	        packs="".join(line[1:-1])
	        line=[packs,line[-1]]
	        trigger=line[-1]
	        #class name getter
	        class_trigger=trigger.split(";")[0]#.replace("/",".")
	        #method name getter
	        method_name=trigger.split("(")[0].split(">")[1]
	        #type of return getter
	        type_trigger=line[1].split(")")[-1]
	        if len(type_trigger)>1:
		        type_trigger=type_trigger[1:-1].replace("/",".")
	        return [class_trigger,method_name,type_trigger,parameters,params_types],letter
	else:
	        trigger=line.strip("\n").split()[1].strip(",")
	        line=line.split()[-1][1:-1]
	        return [trigger,line],letter#non function strings data
	     	
	
#change the line in a file
def change_line(important,line,index_l,letter):
	#find the line number of the enclosing function
	locals_line=find_function_name(important,index_l)
	locals_amount=int(important[locals_line].split()[-1])
	
	#add relevant number of vars to locals and change it
	
	#change enclosing catch
	#catch_to_change=find_function_catch(important,index_l)
	#if catch_to_change!=True:
	#	important[catch_to_change[0]]=catch_to_change[1]
	
	#analyze line to get the parameters, type, class, and method name
	info,letter=analyze_line(line,letter)
	#add metadata to manifest, and add it to the info object
	if letter=="I":#convert to int
	        info[1]=line.split()[-1]
		manifest_id=add_manifest_line_domain(info[1])
	else:	
		manifest_id=add_manifest_line(info[1])
	info[1]=manifest_id
	info.append(locals_amount)
	return info
#add a the application name to manifest
def change_manifest_application(app):
	try:
		pack=""
		with open(app+"/AndroidManifest.xml","r") as r:
			con=r.readlines()
		r.close()
		for i in range(0,len(con)):
			if "<application " in con[i]:
				con[i]=con[i].replace('<application ','<application android:name="PACK.MyApplication" ')
				con[i]=con[i].replace('PACK',pack[1:-1])
				break
			if "package" in con[i]:
				pack=con[i].split("package=")[1].split(">")[0].split()[0]
			
		with open(app+"/AndroidManifest.xml","w") as w:
			for i in con:
				w.write(i)
		w.close()
		path=app+"/smali/"+pack[1:-1].replace(".","/")+"/"
		os.system("cp "+"helpers/MyApplication.smali "+path+"MyApplication.smali")
		with open(path+"MyApplication.smali") as f:
		            newText=f.read().replace('X/', "L"+pack[1:-1].replace(".","/")+"/")
		with open(path+"MyApplication.smali", "w") as f:
		            f.write(newText)
		return path
        except Exception as e:
	        exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print exc_type,exc_obj, fname, exc_tb.tb_lineno
                #shutil.rmtree(app_name)#remove app open pack
                exit(0)
#add a meta-data line to manifest
def change_manifest_metadata(line):
	index=-1
	try:
		global package_name
		with open(package_name+"/AndroidManifest.xml","r") as r:
			con=r.readlines()
		r.close()
		for i in con:
			if "<app" in i:
				index=con.index(i)
				break
		con.insert(index+1,line+"\n")
		with open(package_name+"/AndroidManifest.xml","w") as w:
			for i in con:
				w.write(i)
		w.close()
	except Exception as e:
                
	        exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print exc_type, fname,exc_obj, exc_tb.tb_lineno

                return
#alternative manifest permissions change
def change_manifest_specific_permissions_alternative(group_dict,permissions,package_name):
	try:
		#open the groups file
		
		#open manifest file
		with open(package_name+"/AndroidManifest.xml","r") as r:
			con=r.readlines()
		r.close()
		#iterate the permissions data in manifest
		for i in range(0,len(con)):
			if "<uses-permission" in con[i]:
				#loop the permissions to find if there is a need of group
				for p in permissions:
					if p in con[i]:
					        #try:
						
						        #check=group_dict[p]
						        #if check.startswith("NO"):#no group found
						con[i]=con[i].replace("uses-permission ","uses-permission-sdk-23 ")
						#        else:
						#	        con[i]=con[i].replace(p,group_dict[p])
						#        break
						#except:
						#                con[i]=con[i].replace("uses-permission ","uses-permission-sdk-23 ")
		
		with open(package_name+"/AndroidManifest.xml","w") as w:
			for i in con:
				w.write(i)
		w.close()
	except Exception as e:
                
	        exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print exc_type, fname,exc_obj, exc_tb.tb_lineno
                return
#change speficic permission tag
def change_manifest_intent_actions(intent_actions,package_name):
	print package_name
	intents_check=[]
	try:
		namespace='xmlns:xi="http://www.w3.org/2001/XInclude"'
		include_string='<xi:include href="assets/FILE.xml"/>'
		acts={}
		for i in intent_actions:
			intents_check.append(i)
			f_name=i.split(".")[-1].split('"/')[0]
			f_string=include_string.replace('FILE',f_name)
			acts[i]=f_string
			with open(package_name+"/assets/"+f_name+".xml","w") as w:
				w.write(i)
			w.close()
			
		
		with open(package_name+"/AndroidManifest.xml","r") as r:
			con=r.readlines()
		r.close()
		#add namespace
		for i in range(0,len(con)):
			if "<manifest " in con[i]:
				if namespace not in con[i]:
					con[i]=con[i].replace("<manifest ", "<manifest "+namespace+" ")
				break	
		#change intents
		for i in range(0,len(con)):
			line=con[i].strip()
			if line in intents_check:
				con[i]=con[i].replace(line,acts[line])
				
		with open(package_name+"/AndroidManifest.xml","w") as w:
			for i in con:
				w.write(i)
		w.close()
		
	except Exception as e:
                
	        exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print exc_type, fname,exc_obj, exc_tb.tb_lineno

                return


#change specific type
def check_specific_type(comp_type,comps,package_name):
	try:
		namespace='xmlns:xi="http://www.w3.org/2001/XInclude"'
		include_string='<xi:include href="assets/FILE.xml"/>'
		with open(package_name+"/AndroidManifest.xml","r") as r:
			con=r.read()
		r.close()
		soup = BeautifulSoup(con,'xml')
		check=soup.find_all(comp_type)
		results=[r for r in check if r['android:name'].lower() in comps]
		for i in range(0,len(results)):
			f_name=results[i]['android:name'].replace(".","_")
			with open(package_name+"/assets/"+f_name+".xml","w") as w:
				w.write(str(results[i]))
			w.close()
		#test
		with open(package_name+"/AndroidManifest.xml","r") as r:
			con=r.readlines()
		r.close()
		for i in range(0,len(results)):
			test=str(results[i]).splitlines()
			first_in_test=test[0]
			test_len=len(test)
			name_test=results[i]['android:name'].replace(".","_")
			#add namespace
			include_tag=include_string.replace('FILE',name_test)
			#find the location for change
			ind=0
			for ind in range(0,len(con)):
				line=con[ind].strip()
				if line==first_in_test:
				        try:
					        con[ind]=con[ind].replace(line,include_tag)
					        del con[ind+1:ind+test_len]
					        break
					except:
					        continue
			
		with open(package_name+"/AndroidManifest.xml","w") as w:
			for i in con:
				w.write(i)
		w.close()
	except Exception as e:
                
	        exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print exc_type, fname, exc_tb.tb_lineno

                return 0
                
#check all components
def check_components(lines,package_name):
	
	recs=[]
	sers=[]
	acs=[]
	perms=[]
	for l in lines:
		if "permission" in l:
			perms.append(l)
			continue
		if "broadcastreceiverlist_" in l:
			recs.append(l.split("_")[1])
			continue
		if "activitylist_" in l:
			acs.append(l.split("_")[1])
			continue
		if "servicelist_" in l:
			sers.append(l.split("_")[1])
			continue
	try:
		check_specific_type('receiver',recs,package_name)
		check_specific_type('uses-permission',perms,package_name)
		check_specific_type('service',sers,package_name)
		check_specific_type('activity',acs,package_name)
		
	except Exception as e:
                
	        exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print exc_type, fname, exc_tb.tb_lineno

                return 0



#this function changes the manifest according to the function we encrypt
def add_manifest_line(function):
	try:
		global package_name
		with open(package_name+"/AndroidManifest.xml","r") as r:
			con=r.read()
		r.close()
		data='    <meta-data android:name=FUN android:value=?/>'
		encoded = base64.b64encode(function)
		soup = BeautifulSoup(con,'xml')
		check=soup.find_all('meta-data')
		if check:
		        try:
		                c=[c for c in check if c['android:value']==encoded]
		                if c:
			                return c[0]['android:name']
			except:
			        pass
		ID=randomStringDigits()
		data=data.replace("FUN",'"'+ID+'"')
		data=data.replace("?",'"'+encoded+'"')
		change_manifest_metadata(data)
		return ID
	except Exception as e:
                
	        exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print exc_type, fname, exc_tb.tb_lineno

                return 0
#this function changes the manifest according to the function we encrypt
def add_manifest_line_domain(function):
	try:
		global package_name
		with open(package_name+"/AndroidManifest.xml","r") as r:
			con=r.read()
		r.close()
		data='    <meta-data android:name=FUN android:value=?/>'
		soup = BeautifulSoup(con,'xml')
		check=soup.find_all('meta-data')
		encoded=function.replace("http","attp").replace('\"','')
        	encoded = encoded.replace(".", "%%%%")
		if check:
		        try:
		                c=[c for c in check if c['android:value']==encoded]
		                if c:
			                return c[0]['android:name']
			except:
			        pass
		ID=randomStringDigits()
		data=data.replace("FUN",'"'+ID+'"')
		data=data.replace("?",'"'+encoded+'"')
		change_manifest_metadata(data)
		return ID
	except Exception as e:
                
	        exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print exc_type, fname, exc_tb.tb_lineno

                return 0
#random ID
def randomStringDigits(stringLength=10):
    """Generate a random string of letters and digits """
    lettersAndDigits = string.ascii_letters + string.digits
    return ''.join(random.choice(lettersAndDigits) for i in range(stringLength))
#ip to long
def ip2long(ip):
    """
    Convert an IP string to long
    """
    
    packedIP = socket.inet_aton(ip)
    return struct.unpack("!L", packedIP)[0]    

