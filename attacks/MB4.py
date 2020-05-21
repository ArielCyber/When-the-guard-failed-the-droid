import os
import sys
import time
import glob
import shutil

def end_file_process(f,folder,i):#sign and copy apk
	f=f.split('/')[1].split(".apk")[0]
	os.system("apktool b "+f)#+" 2>&1")
	file_to_sign=f+"/dist/"+f+".apk"
	os.system("jarsigner -verbose -sigalg SHA1withRSA -digestalg SHA1 -storepass apkkey -keystore apkkey.keystore "+file_to_sign+" alias_name >> tmp.csv")
	os.remove("tmp.csv")
	os.system("cp "+file_to_sign+" "+folder+"/"+i)#copy to new apks
	shutil.rmtree(f)#remove app open pack

def open_apk(f):#read the manifest
	os.system("apktool -f d "+f)#open apk
	folder_name=f.split('/')[1].split(".apk")[0]
	with open(folder_name+"/AndroidManifest.xml","r") as r:
		content=r.readlines()
	r.close()
	return content,folder_name

def write_attack(content,folder_name,f,output,i):#create clear manifest
	os.remove(folder_name+"/AndroidManifest.xml")

	with open(folder_name+"/AndroidManifest.xml", "w") as w:
		for c in content:
			w.write(c)
	end_file_process(f,output,i)

#read stats
with open("statistics.csv","r") as r:
	cont=r.readlines()
r.close()
by_mal=[]
by_ben=[]
for i in cont[1:]:
	line=i.split("{")
	line=line[2].split("}")
	family=line[0]
	stats=line[1].split(",")[1:3]
	benign=float(stats[0])
	by_ben.append([benign,family])
by_ben.sort(reverse=True)
perms_updated=[]
#need to be upgraded if families are in order
for p in by_ben[0:3]:
	ar_perms=[]
	temp_perms=p[1].split(",")
	for t in temp_perms:
		t=t.strip(" ").strip('"').strip("'")
		ar_perms.append('android.permission.'+t)
	perms_updated.append(ar_perms)

def get_applications(PATH_TO_FILES):
	files=[]
	for i in range(0,5):
		P=PATH_TO_FILES.replace("_i","_"+str(i))
		for path, subdirs, files_w in os.walk(P):
			for name in files_w:
				n=os.path.join(path, name)
				if not n.endswith(".apk"):
					continue
				files.append(n)
	return files

def get_applications_allready(PATH_TO_FILES):
	files=[]
	for path, subdirs, files_w in os.walk(PATH_TO_FILES):
		for name in files_w:
			n=os.path.join(path, name)
			if not n.endswith(".apk"):
				continue
			splits=n.split("_")
			files.append("malware_"+splits[1].replace("attack/","")+"/"+splits[2])
	return files

PATH_TO_FILES="malware_i/"
files=get_applications(PATH_TO_FILES)
get_allready_done=get_applications_allready("blind_attack/")
files=list((set(files)-set(get_allready_done)))
#create attack dirs
'''
if not os.path.exists("blind_attack"):
    os.makedirs("blind_attack")
if not os.path.exists("statistic_attack"):
    os.makedirs("statistic_attack")
'''
#iterate files
for f in files:
	try:
		i=f.split("malware_")[1].replace("/","_")
		#first attack
		content,folder_name=open_apk(f)#read the apk
		for c in range(0,len(content)):
			if "uses-permission " in content[c]:
				content[c]=content[c].replace("uses-permission ","uses-permission-sdk-23 ")
		write_attack(content,folder_name,f,"blind_attack",i)
		#second attack
		content,folder_name=open_apk(f)#read the apk

		#get a list of all permissions
		current_app_perms={}
		for c in range(0,len(content)):
			if "uses-permission " in content[c]:
					perm_temp=content[c].split('android:name=')[1].split('/')[0][1:-1]
					current_app_perms[perm_temp]=0
		#check for a family
		perms_updated_check_family=[x for x in perms_updated if len(x)>1]
		#leave the families out of the permission list check(length 1 of a family)
		perms_updated=[x for x in perms_updated if x not in perms_updated_check_family]
		#create a dict of permissions of the app
		for p in perms_updated_check_family:
			for elem in p:
				current_app_perms[elem]=1
		#change the permissions to sdk-23 if needed
		for c in range(0,len(content)):
			if "uses-permission " in content[c]:
					perm_temp=content[c].split('android:name=')[1].split('/')[0][1:-1]
					if current_app_perms[perm_temp]==0:#not a member of the family with more than one member
						if perm_temp not in perms_updated:#not a member of family with one member
							content[c]=content[c].replace("uses-permission ","uses-permission-sdk-23 ")
		#check if the family exists in the app-if not-create it
		if not sum(current_app_perms.values())==sum(len(x) for x in perms_updated_check_family):# add another member to the family if not all the family is here
			keys=[k for k,v in current_app_perms.items() if v == 1]
			for k in keys:
				for c in range(0,len(content)):
					if "uses-permission " in content[c]:
						content.insert(c,'<uses-permission android:name="'+k+'"/>')
						break
		write_attack(content,folder_name,f,"statistic_attack",i)
	except:
		continue
