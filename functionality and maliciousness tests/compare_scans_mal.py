#!/usr/bin/python
from __future__ import division
import sys
import numpy as np
origs=[]
manips=[]
origs_rates={}
manips_rates={}
with open(sys.argv[1],'r') as r:
	origs=r.readlines()
r.close()
with open(sys.argv[2],'r') as r:
	manips=r.readlines()
r.close()

for i in origs:
	i=i.split(",")
	name=i[0].split("/")[-1]
	
	if name in origs_rates:
		continue 
	try:
		origs_rates[name]=[i[1],i[2]]
	except:
		
		continue

for i in manips:
	i=i.split(",")
	name=i[0].split("/")[-1].split("_")[-1]
	if name in manips_rates:
		continue
	try:
		manips_rates[name]=[i[1],i[2]]
	except:
		continue
avg=0
count=0
count_fault=0
vals=[]
count_total=0
flaws=[]

for k in manips_rates.keys():
	count_total+=1
	try:
		spec_dif=-int(origs_rates[k][0])+int(manips_rates[k][0])
		vals.append(spec_dif)
		print k, int(origs_rates[k][0]), int(manips_rates[k][0]), spec_dif#get how much the manipulation works on scanners
	
		avg+=spec_dif
		count+=1
	except:
		exit(0)
		count_fault+=1
		flaws.append(k)
		continue
#for i in origs:
#	for f in flaws:
#		if f in i:
#			print i
print len(manips_rates)
print "average difference between manipulated and original: "+str(avg/count)
print "std of files: "+str(np.std(vals))
print "faulty apps: ", count_fault, count_fault/count_total
