#!/usr/bin/python
from __future__ import division
import sys
import numpy as np
	
def read_file(f):
	files_array=[]
	with open(f,'r') as r:
		content=r.readlines()
	r.close()
	for i in content:
		i=i.split(" ")
		name=i[0]
		sign=int(i[1])
		files_array.append([name,sign])
	return files_array
	
origs=read_file(sys.argv[1])
mainpulated=read_file(sys.argv[2])
new_origs=[]
j=0
for i in range(0,len(mainpulated)):
	test=mainpulated[i][0]
	while origs[i][0]!=test:
		del origs[i]

counter=[0,0,0,0]
total=0
total_works=0
for o in origs:
	ind=o[1]
	counter[ind]+=1
	total+=1
	if ind<2:
		total_works+=1

counter2=[c/total_works for c in counter][0:2]
counter=[c/total for c in counter]
print "for the pre manipulated apps:", counter, total
print "for the pre manipulated apps:", counter2,total_works
counter=[0,0,0,0]
total=0
total_works=0
for o in mainpulated:
	ind=o[1]
	counter[ind]+=1
	total+=1
	if ind<2:
		total_works+=1
counter2=[c/total_works for c in counter][0:2]		
counter=[c/total for c in counter]

print "for the post manipulated apps:", counter, total
print "for the post manipulated apps:", counter2,total_works
	
