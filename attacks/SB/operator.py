from __future__ import division
import os
import sys
import time
from shutil import move
from shutil import copyfile

root="/media/cyberlab/Backup_Ariel/datasets"
Malware_train=root+"/mals/"+str(sys.argv[1])+"/train"
Benign_train=root+"/ben_train"
Malware_test=root+"/mals/"+str(sys.argv[1])+"/test"
Benign_test=os.getcwd()+"/ben"

#Malware_test="/home/cyber/robust_apk_detection/attack/malware"


start=time.time()
os.chdir("Drebin")
#First, run Drebin on the dataset
os.system("python Main.py --holdout 1 --testmaldir "+Malware_test+" --testgooddir "+Benign_test+" --maldir "+Malware_train+" --gooddir "+Benign_train)
copyfile("explanations_HC.json", "../explanations_former.json")#copy the weights
os.chdir("../")
#Then, get the dataset report from it,for each app
with open("Drebin/class_report.csv","r") as r:
        report=r.readlines()
r.close()
os.rename('Drebin/class_report.csv', 'Drebin/class_report_former.csv')
#read data from the report
mal_files_in_data=0
mal_files_to_manip=0
files_for_attack=[]
#create the dir of malware
directory="malware"
if not os.path.exists(directory):
    os.makedirs(directory)
#take the files that were identified
for line in report:
        line=line.split(",")
        name=line[0]
        truth=float(line[1])
        label=float(line[2])
        if truth==1:
                mal_files_in_data+=1
                if truth==label:#Drebin failed
                        files_for_attack.append(name.split(".")[0])
                        mal_files_to_manip+=1

prec_mal=mal_files_to_manip/mal_files_in_data       
#Then, run the attack on the apps that were identified correctly

for f in files_for_attack:
        try:
                os.system("cp "+f+".apk"+" malware/")
        except:
                continue


new_folder="weight_"+sys.argv[2].replace(".","")
os.mkdir(new_folder)

os.system("python read_disect.py malware/ "+str(sys.argv[2]))
#check the files again

os.chdir("Drebin")

os.system("python Main.py --holdout 1 --testmaldir ../generated_apks --testgooddir "+Benign_test+" --maldir "+Malware_train+" --gooddir "+Benign_train)
os.chdir("../")
#move important files
new_folder="subtle_manip"
os.mkdir(new_folder)
move("generated_apks",new_folder+"/")
move("Drebin/class_report.csv",new_folder+"/")
copyfile("Drebin/explanations_HC.json",new_folder+"/")
#Then, take part of the evaded apps and integrate them in the test data and test against other that were
#evasion' processed
mal_files_in_data=0
mal_files_to_manip=0
files_for_attack=[]
with open(new_folder+"/class_report.csv","r") as r:
        report=r.readlines()
r.close()
for line in report:
        line=line.split(",")
        name=line[0]
        truth=float(line[1])
        label=float(line[2])
        if truth==1:
                mal_files_in_data+=1
                if truth==label:#Drebin failed
                        files_for_attack.append(name.split(".")[0])
                        mal_files_to_manip+=1

prec_mal2=mal_files_to_manip/mal_files_in_data
#print prec_mal,prec_mal2#, prec_mal2   
end=time.time()
print "overall running time: "+str(end-start)+ " seconds"
