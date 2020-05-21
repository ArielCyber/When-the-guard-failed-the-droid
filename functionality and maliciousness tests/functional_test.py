# HAREL's CODE for android emulator
import sys
import shutil
from androguard.core.bytecodes import dvm
from androguard.core.analysis import analysis
from androguard.misc import AnalyzeAPK, AnalyzeDex
import os
import time
import subprocess


def run_application_checks(PATH_TO_FILES,results_file):
	files=[]
	for i in range(0,5):
		P=PATH_TO_FILES.replace("_i","_"+str(i))
		for path, subdirs, files_w in os.walk(P):
			for name in files_w:
				n=os.path.join(path, name)
				if not n.endswith(".apk"):
					continue
				files.append(n)
	results=open(results_file,"a",buffering=0)#open the results file 
	#loop the files

	for f in files:
		subprocess.Popen("adb logcat -b all -c", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		try:
			a, d, dx = AnalyzeAPK(f)
			package_name=a.get_package()
			os.system("adb install "+f)#install the app
			p = subprocess.Popen("adb shell pm dump "+package_name+" | grep -A 1 MAIN",shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]#+" | grep -A 1 MAIN", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]
			lines=p.split("\n")
			#print lines
			intent_main="android.intent.action.MAIN:"
			activity_name=""
			activity_check=0
			#get the main activity
			for line in lines:
				if intent_main in line:
					index=lines.index(line)
					opts=lines[index+1].split(" ")
					for option in opts:
						if option.startswith(package_name):#found the activity name
							activity_name=option
							activity_check=1
							break 
					break
	
			if activity_check==1:
				try:
				
					os.system("adb shell am start -a android.intent.action.MAIN -n "+activity_name)#run the app
					time.sleep(1.5)
					out = subprocess.Popen("adb logcat -d", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]
					lines=out.split("\n")
					dictOfLines = { l : 0 for l in lines}
					if "--------- beginning of crash" in dictOfLines:
							results.write(package_name+" 1\n")
					
					else:
						results.write(package_name+" 0\n")
					os.system("adb shell am force-stop "+package_name)#stop the app
					
				except:
					results.write(package_name+" 3\n")
			else:
				results.write(package_name+" 2\n")
			subprocess.Popen("adb logcat -b all -c", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			os.system("adb shell pm uninstall "+package_name)
		except:
			subprocess.Popen("adb logcat -b all -c", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			os.system("adb shell pm uninstall "+package_name)
			continue
	#os.system("adb kill-server")
root="/home/harel/functional_maliciousness_tests/malware_directory/"
root_files="/home/harel/functional_tests/evaluations/journal"
PATH_NO_SMALI=root+"no_smali/no_smali_i/generated_apks"
PATH_INIT=root+"initial_malware/malware_i/"
PATH_WEIGHT=root+"by_weight/weight_0/weight_0_i/generated_apks"
PATH_TEST="/home/harel/functional_maliciousness_tests/malware_directory/no_smali/no_smali_0"
PATH_BLIND="/home/harel/functional_maliciousness_tests/malware_directory/blind/bl_i/blind_i"
PATH_STAT="/home/harel/functional_maliciousness_tests/malware_directory/statistic/statistic_attack_i"
'''
start=time.time()
subprocess.Popen("adb logcat -b all -c", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
run_application_checks(PATH_BLIND,"blind.csv")
end=time.time()
print end-start	
exit(0)
'''
start=time.time()
subprocess.Popen("adb logcat -b all -c", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
time.sleep(1)
run_application_checks(PATH_STAT,"statistic_func.csv")
end=time.time()
print end-start	

