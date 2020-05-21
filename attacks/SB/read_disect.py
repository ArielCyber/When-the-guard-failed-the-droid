import sys
import os
import glob
from manifest_mediator import *
import shutil
import json
import time
from shutil import copytree
#remove all mal snippets
def rem(pat,fold):
        import os, re, os.path
        pattern = pat
        mypath = fold
        for root, dirs, files in os.walk(mypath):
            for file in filter(lambda x: re.match(pattern, x), files):
                os.remove(os.path.join(root, file))


mals=sys.argv[1]#malware directory
files=[]
reports=[]

for filename in glob.glob(mals+'*.apk'):
	f=filename.split(".")[0]
	files.append(f+".apk")
	#reports.append(f+".data")

generated=[]	
if not os.path.exists("generated_apks"):
    os.makedirs("generated_apks")
else:
        generated=set(os.listdir("generated_apks"))

#dict of permissions
PERM_D="SmallCasePScoutPermApiDict.json"
with open(PERM_D,"r") as r:
	con=r.read()
r.close()
'''with open("danger.csv","r") as r:
	dangers=r.readlines()
r.close()
dangers=[d.strip() for d in dangers]'''
t=json.loads(con)
Permissions_dict={}
keys=t.keys()
for k in keys:
	#if k.split(".")[-1] not in dangers:
	#	continue 
	for p in t[k]:
		content=p[0].replace(".","/")+"."+p[1]
		try:
			Permissions_dict[k].append(content)
		except:
			Permissions_dict[k]=[content]


PATH="explanations_former.json"
with open(PATH,"r") as r:
	con=r.read()
r.close()
limit=float(sys.argv[2])
t=json.loads(con)
features_dict={}
for p in t:
	orig=int(t[p]['original_label'])
	pred=int(t[p]['predicted_label'])
	if orig==1 and pred==1:
	        app_name=p.split(".")[0]
		features_dict[app_name]=[]
		for k in t[p]['top_features']:
		        weight=float(k[0])
		        if weight>limit:
	                        features_dict[app_name].append(k[1])

with open("permission_to_groups.txt","r") as dan:
	g=dan.readlines()
dan.close()
#create a dictionary of permission->group_name
name=""
group_dict={}
for line in g:
	if "Permissions" in line:
		continue
	if ":" in line:
		name=line.strip(":\n").replace("-group","")
		
	group_dict[line.strip("\n")]=name
			
#loop the data and update attack
max_count=0
not_manip_yet=[]
for index in range(0,len(files)):
	f=files[index].split("/")[-1]
	if f not in generated:
		not_manip_yet.append(files[index])
files=not_manip_yet		
action_template='<action android:name="ACTION"/>'
#loop over files
count=0	
for index in range(0,len(files)):
	count+=1
	if count>1:
		break
        try:
                
	        app_name=files[index].split("/")[1].split(".apk")[0]
	        root= app_name+"/smali/"
	        sus_api=[]
	        non_func=[]
	        ips=[]
	        includes=[]
	        comps=[]
		permissions_to_update=[]
	        #get objectives

	        for line in features_dict[app_name]:
	        	line=json.dumps(line)
	        	line=line[1:-1]
	        	#permission apis check
	        	if "intentfilterlist_" in line:
				continue
	        		intent=line.split("intentfilterlist_")[1].strip("\n")
	        		intent=intent.replace(intent.split(".")[-1],intent.split(".")[-1].upper())
	        		action_template_spec=action_template.replace("ACTION",intent)
	        		includes.append(action_template_spec)
	                	continue
	                if "requestedpermissionlist_" in line:
                                continue
	        		perm=line.split("requestedpermissionlist_")[1].strip("\n")
	        		permissions_to_update.append(perm)
	                	continue
	        	#permission apis check
	        	if "usedpermissionslist_" in line:
	        		perm=line.split("usedpermissionslist_")[1].strip("\n")
	        		try:
	                		for permission in Permissions_dict[perm]:
	                			sus_api.append(permission.strip("\n").replace(".",";->"))
	                	        continue
	                	except:
	                	        continue
	             	#suspicous api check
		        if "suspiciousapilist_" in line:

		                if "httppost" in line:
		                        continue
			        if not "." in line:
			                if ";->" in line:
			                        sus_api.append(line.split("suspiciousapilist_")[1].strip())

			                else:
			                	if not "suspiciousapilist_L" in line:
			                		non_func.append(line.split("suspiciousapilist_")[1].strip())
			                	else:
			                        	continue
			        else:
			                sus_api.append(line.split("suspiciousapilist_")[1].strip().replace(".",";->"))
			        continue
			#restricted api check
			if "restrictedapilist_" in line:

			        li=line.split("restrictedapilist_")[1].strip().split(".")
			        func=";->"+li[-1]
			        li="/".join(li[:-1])+func
			        sus_api.append(li)
			        continue
			#url check
			if "urldomainlist_" in line:
                                continue
			        li=line.split("urldomainlist_")[1].strip()
			        ips.append(li)
			        continue
			comps.append(line)
	        r.close()

	        #open the apk
	        smali_files=[]
	        #open the apk
	        os.system("apktool -f d "+files[index]+" >> tmp.csv" )
		try:
			copytree(files[index].split("/")[1].split(".apk")[0],"former")	
		except:
			shutil.rmtree("former")
			copytree(files[index].split("/")[1].split(".apk")[0],"former")	
	        os.remove("tmp.csv")
	        #change permission in the manifest
	        specific_permissions=[permission.replace(permission.split(".")[-1],permission.split(".")[-1].upper()) for permission in  permissions_to_update]
		
	        #change permission in manifest
	        change_manifest_specific_permissions_alternative(group_dict,specific_permissions,app_name)
	        #include manifest components
	        #change_manifest_intent_actions(includes,app_name)
		path_to_context=change_manifest_application(app_name)
		path_to_context="Lcom"+path_to_context.split("/com")[1]
	        #components
		#check_components(permissions_to_update,app_name)
	        #check_components(comps,app_name)

		
	        #list all apk files in perm_files.csv
	        with open("perms_files.csv","w") as w:
		        #list all the files in the apk
		        for path, subdirs, files_w in os.walk(root):
		           	for name in files_w:
				        w.write(os.path.join(path, name)+"\n")				
	        w.close()
		start=time.time()     
	        #let's look on the files and permissions
	        with open("perms_files.csv","r") as r:	
		        important_files=r.readlines()
	        r.close()
	        for i in important_files:
		        i=i.strip()
		        #get a copy of the malware snippet
		        for s in sus_api:
			        check_lines(i,s,app_name,"F",path_to_context)
			for n in non_func:
			        check_lines(i,n,app_name,"N",path_to_context)
			for ip in ips:
			        check_lines(i,ip,app_name,"I",path_to_context)
	
	        os.remove("perms_files.csv")
	        rem("clinit_non_func.smali",root)#remove obselete snippet
	        rem("clinit.smali",root)#remove obselete snippet
	        rem("clinit_no_args.smali",root)#remove obselete snippet
	        #build and sign apk
		while True:
			os.system("apktool b "+app_name+" 2> err.log")

			if os.stat("err.log").st_size!=0:
				with open("err.log","r") as r:
					er=r.readlines()
				r.close()
				for elem in er:
					file_er=elem.split("[")[0]
					try:
						line=int(elem.split("[")[1].split(",")[0])
						break
					except:
						continue
				try:#check if there was an error we can fix
					if float(line).is_integer():
						pass
				except:
					break
				
				former_file="former/"+"/".join(file_er.split("/")[1:])
				try:
					with open(file_er,"r") as r_manip:
						lines_manip=r_manip.readlines()
					r_manip.close()
				except IOError as e:
					print elem
					break
				with open(former_file,"r") as r_former:
					lines_former=r_former.readlines()
				r_manip.close()
				
				index_in_manip=find_function_declaration(lines_manip,line)
				end_in_manip=find_string(lines_manip,line,".end method")
				index_in_orig=find_string(lines_former,0,lines_manip[index_in_manip])
				end_in_orig=find_string(lines_former,index_in_orig,".end method")
				lines_manip=lines_manip[:index_in_manip]+lines_former[index_in_orig:end_in_orig+1]+lines_manip[end_in_manip+1:]
				
				with open(file_er,"w") as w:
					for i in lines_manip:
						w.write(i+"\n")
				
			else:
				break
		shutil.rmtree("former")
		end=time.time()
		os.remove("err.log")
		print "running time: "+str(end-start)
	        file_to_sign=app_name+"/dist/"+app_name+".apk"
	        os.system("jarsigner -verbose -sigalg SHA1withRSA -digestalg SHA1 -storepass apkkey -keystore helpers/apkkey.keystore "+file_to_sign+" alias_name >> tmp.csv")
	        os.remove("tmp.csv")
	        os.system("cp "+file_to_sign+" generated_apks/"+app_name+".apk")#copy to new apks
	        exit(0)
	        shutil.rmtree(app_name)#remove app open pack
	        
	except Exception as e:
	        exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print exc_type,exc_obj, fname, exc_tb.tb_lineno
                #shutil.rmtree(app_name)#remove app open pack
                continue
                

