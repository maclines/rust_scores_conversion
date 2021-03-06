#!/usr/bin/env python
import os
import re
import sys
import argparse

parser = argparse.ArgumentParser (description = "python convert_rust_reading_seedling.py --typo sample_data_seedling/typo.seedling.txt --PHENO  sample_data_seedling/TCAP_seedling.txt --columns 7,9")
parser.add_argument ('-t','--typo_f', help ="typo file, you can use the one supplied in the sample data folder")
parser.add_argument ('-p', '--PHENO', help ="phenotype file, tab delimited, ending with .txt, see sample_data for example")
parser.add_argument ('-c', '--columns', help ="columns of data to be converted, should be comma delimited, such as '3,4,5'")

if len(sys.argv)==1:
    parser.print_help()
    sys.exit(1)

args = parser.parse_args()

if os.path.exists(args.typo_f) and os.path.getsize(args.typo_f) > 0:
    typo_f=args.typo_f
else:
    sys.exit('the typo file is not thre! you can use the one in sample data folder')
if os.path.exists(args.PHENO) and os.path.getsize(args.PHENO) > 0:
    PHENO=args.PHENO
else:
    sys.exit('the phenotype file is not thre! provide tab delimited pheno file, ending .txt')
if re.search(r'[0-9]',args.columns):
    cols=args.columns
else:
    sys.exit("he columns should be specified! use coma separated values such as '3,4,5'")



###### 1. typo conversion

def convert_typo(read):
    IN = open (typo_f, 'rU') ### This file should have 2 columns, col1 is typo, col2 is the standardized (correct) reading
    typo_dict = dict()
    for line in IN:
        line = line.strip("\r\n")
        F = line.split(); 
        typ = F[0]; std=F[1]
        if len(F) == 2:
            typo_dict[typ] = std
    if read in typo_dict.keys():
        read = typo_dict[read]
    return read
        
# print convert_typo("5") ### there should never be a 5 for IT (0-4 scale), 5 will be converted to NA
# print convert_typo("3+")


##2. convert IT (infection type)
def convert_IT (IT):
    IT = IT.replace('\r\n','')
    orig_it = IT
    IT = convert_typo(IT)
    IT = IT.upper()
    if re.search('NA',IT):
        num_IT = "NA"
    elif re.search('[01234\;]',IT):
        IT = re.sub('\s+',"", IT)
        IT = re.sub ('\/',"", IT)
        IT = re.sub(r'[A-Z]','',IT) ## fix a minor bug, there should not be letters....rm all
        IT = IT.replace("1-", 'a')
        IT = IT.replace("1+", 'b')
        IT = IT.replace("2-", 'c')
        IT = IT.replace("2+", 'd')
        IT = IT.replace("3-", 'e')
        IT = IT.replace("3+", 'f')
        fields = list(IT)
        fields = [fields[0]] + fields ### double weight the first element
        dict_IT = {'0':0, ';':0, 'a':1, '1':2, 'b':3, 'c':4,'2':5,'d':6,'e':7,'3':8,'f':9,'4':9}
        numbers =list()
        for num in fields:
            if dict_IT.has_key(num):
                numbers.append(dict_IT[num])
        if len(numbers) >0:
            num_IT = sum(numbers)/float(len(numbers))
            num_IT = round (num_IT, 2)  ###  rouding to 2 decimal points
    else:
        num_IT = "NA"
    return num_IT
        
# print convert_IT('4   3-3+2-;')

#3 main program

PHENO_OUT = PHENO.replace (".txt", ".python.out.txt")

cols = re.sub('\s+','',cols)   ### remove extra spaces if any (in column specification)
if re.search(',', cols):  ### if column numbers were specified with comma, split 
    cols = cols.split(","); 
    for i in range(len(cols)):
        cols[i]=int(cols[i])
else:
    cols =[int(cols)]   ### if there is only one value for column specification, cols =[cols]

########## assign cols using ARGV or mannually such as here.

InPheno = open (PHENO, 'rU')
out_file = open (PHENO_OUT, 'w')

header = InPheno.readline()  ### remove header
header = header.strip('\r\n')
F = header.split("\t")

for col in cols:
    F[col] = F[col]+"\t"+F[col]+".num"
print >>out_file, "\t".join(F)

for Line in InPheno:
    Line = Line.strip ('\r\n')
    F = Line.split("\t")
    for col in cols:
        IT = F[col]
        num_IT = convert_IT (IT)
        F[col] = IT+"\t"+str(num_IT)
    new_Line = "\t".join(F)
    print >>out_file, new_Line

InPheno.close()
out_file.close()    

