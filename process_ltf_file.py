# process a single ltf file (as opposed to a directory, which preprocessing-test.py does) and outputs just the text
# If given a list of exclude document and segment ids, it will exclude segments from those ids

import os
from os.path import basename
import csv
import codecs
import sys

def read_excluded_ids(exclude_file):
    ef = codecs.open(exclude_file,'r','utf-8')
    excluded=[]
    for line in ef:
        line=line.strip()
        docid, segment = line.split('\t')
        #print(docid, segment)
        excluded.append((docid, segment))
    return excluded

if len(sys.argv) < 3:
    sys.exit("Please specify an input xml file and output directory")

# Run like this: 
# python process_ltf_file.py /proj/nlp/corpora/SEEM/text/LDC2017E27_LORELEI_IL5_Incident_Language_Pack_for_Year_2_Eval_V1.1/set0/data/translation/comparable/eng/ltf/ENG_DF_000183_20120305_C0001Z0JE.ltf.xml 
#/proj/nlp/corpora/SEEM/text/LDC2017E27_LORELEI_IL5_Incident_Language_Pack_for_Year_2_Eval_V1.1/set0/data/translation/comparable/eng-txt
# /proj/nlp/users/noura/LORELEI/eval/monolingual/ti/in_eval.ti.txt
    
input_file = sys.argv[1]
output_dir = sys.argv[2]
excluded_ids = []
if len(sys.argv) == 4:
    print("Reading excluded ids")
    excluded_ids = read_excluded_ids(sys.argv[3])
out_file = os.path.join(output_dir, basename(input_file) + '.txt')
f = codecs.open(input_file,'r')
tsvf = codecs.open(out_file,'w')
docid = ""
for line in f:
    if line.startswith("<DOC id"):
        fields = line.split(' ')
        docid = fields[1].split('=')[1].replace("\"","")
        print("doc id:", docid)
    elif line[:4] == '<SEG':
        seg = ""
        fields = line.split(' ')
        for field in fields:
            if field.startswith("id="):
                seg = field.split('=')[1]
                seg = seg.replace("\"","")
                break
    elif line[:4] == '<ORI':
        text = line[15:-17]
        print(seg)
        print(text)
        if (docid, seg) in excluded_ids:
            print("Excluding this segment id:", docid, seg)
        else:
            #tsvf.write(fname + '\t' + seg + '\t' + text + '\n')
            tsvf.write(text + '\n')

f.close()
tsvf.close()

        
    


