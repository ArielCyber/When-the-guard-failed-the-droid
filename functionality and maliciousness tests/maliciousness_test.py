#!/usr/bin/python
import os
import time
import requests
import re, hashlib
import json
def checkMD5(checkval):
  if re.match(r"([a-fA-F\d]{32})", checkval) == None:
    md5 = md5sum(checkval)
    return md5.upper()
  else: 
    return checkval.upper()

def md5sum(filename):
  fh = open(filename, 'rb')
  m = hashlib.md5()
  while True:
      data = fh.read(8192)
      if not data:
          break
      m.update(data)
  return m.hexdigest() 

def get_files(PATH):
	files=[]
	for path, subdirs, files_w in os.walk(PATH):
		for name in files_w:
			if not name.endswith(".apk"):
				continue
			files.append(os.path.join(path, name))
	return files

def send_file(file_name):

	url = 'https://www.virustotal.com/vtapi/v2/file/scan'

	params = {'apikey': api}

	files = {'file': (file_name, open(file_name, 'rb'))}

	response = requests.post(url, files=files, params=params)

	#return response.json()

def report_file(f):
	url = 'https://www.virustotal.com/vtapi/v2/file/report'
	md5 = checkMD5(f)
	params = {'apikey': api, 'resource': md5}
	response = requests.get(url, params=params)
	res=response.json()
	try:
		return f+","+str(res["positives"])+","+str(res["total"])+","+str(res["scan_date"])
	except:
		return False
	
def send_files(files):
	
	for f in files:
		try:
			send_file(f)
		except:
			print "error at sending file "+str(files.index(f))
			continue
def report_files(files,file_name):
	for f in files:
		try:
			x=report_file(f)
			file_name.write(x)
			file_name.write("\n")
			#time.sleep(5)
		except Exception as e:
			print "error at report of file "+str(files.index(f))
			continue		
def get_files_i(PATH):
	
	all_files=[]
	for i in range(0,5):
		p=PATH.replace("_i/","_"+str(i)+"/")
		all_files=all_files+get_files(p)
	return all_files
def operation(PATH,f_name):
	
	all_files=[]
	for i in range(0,5):
		p=PATH.replace("_i","_"+str(i))
		all_files=all_files+get_files(p)
	print len(all_files)
	exit(0)
	print "done enumerate files"
	s=time.time()
	send_files(all_files)
	e=time.time()
	
	print "sending_time: "+str(e-s)
	f = open(f_name,'a+')
	report_files(all_files,f)	
def listing(PATH):
	all_files=get_files(PATH)
	send_files(all_files)
	report_files(all_files)	
def listing_partial(PATH,files):
	all_files=get_files(PATH)
	leftovers=[x for x in all_files if x not in files]
	report_files(leftovers)
def listing_from_file(f):
	with open(f,"r") as r:
		content=r.readlines()
	r.close()
	lines=[]
	for i in content:
		lines.append(i.split(",")[0])
	return lines	

def behave(f):

	url = 'https://www.virustotal.com/vtapi/v2/file/behaviour'
	md5 = checkMD5(f)
	params = {'apikey':api,'hash':md5}

	response = requests.get(url, params=params)

	print response

def long_report_file(f):
	url = 'https://www.virustotal.com/vtapi/v2/file/report'
	md5 = checkMD5(f)
	params = {'apikey': api, 'resource': md5,'allinfo': 'true'}
	response = requests.get(url, params=params)
	res=response.json()
	print res
	
api = 'bddd597536b7bbe09384e7a9a4d295e6f90264cf6503b61123096966aa2ce57c'


PATH_NO_SMALI="/home/harel/functional_maliciousness_tests/malware_directory/no_smali/no_smali_i"
PATH_ALL="/home/harel/functional_maliciousness_tests/malware_directory/by_weight/weight_0/weight_0_i"
PATH="/media/harel/Backup_Ariel/datasets/new_attack/bl_i/blind_i/"
PATH_STAT="/media/harel/Backup_Ariel/datasets/new_attack_improved/st_i/statistic_attack_i/"
#operation(PATH_STAT,"statistic_vt.csv")

files=get_files_i(PATH_STAT)
#f = open("statistic_vt_prescan.csv",'a+')
#report_files(files,f)
files_done=listing_from_file("stats_vt.csv")

new_files=[x for x in files if x not in files_done]
for f in new_files:
	print f 
exit(0)
send_files(new_files)
f = open("statistic_vt_scan.csv",'a+')
report_files(new_files,f)
#exit(0)
#operation(PATH,"blind_vt_scan2.csv")
#files1=get_files(PATH1)
#files2=get_files(PATH2)
#send_files(files2)
#report_files(files1)
#report_files(files2)
