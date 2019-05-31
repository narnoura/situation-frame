import os
import csv
import codecs
import sys
#reload(sys)
#sys.setdefaultencoding('utf8')


directory = '/proj/nlp/corpora/SEEM/LDC2017E17_LORELEI_SEC_Pilot_Evaluation_Data/data/monolingual_text_with_tweets/'
out = 'SEC_test_data.txt'

if len(sys.argv)>2:
	directory = sys.argv[1]
	out = sys.argv[2]

tsvf = codecs.open(out,'w','utf8')
files = os.listdir(directory)
for fname in files:
    print(fname)
    f = codecs.open(directory+fname,'r','utf8')
    for line in f:
        if line[:4] == '<SEG':
            #seg = line.split('"')[1]
            seg = ""
            fields = line.split(' ')
            for field in fields:
                if field.startswith("id="):
                    seg = field.split('=')[1]
                    seg = seg.replace("\"","")
                    break
        if line[:4] == '<ORI':
            text = line[15:-17]
            print(seg)
            print(text)
            tsvf.write(fname + '\t' + seg + '\t' + text + '\n')
            #row = []
            #row.append(fname)
            #row.append(seg)
            #row.append(text)
            #writer.writerow(row)
    f.close()
tsvf.close()
#csvf.close()
