# Select only the docs that are in dev for running situation towards frame on dev.
# Run like this: python select-dev.py <dev_file> <selected_sentiment_segments>
# Since the dev set doesn't contain all the frames/segments from the doc, also keep only the segments that are in dev file (# that includes the none segments)

import json
import sys
import os


if len(sys.argv)<3:
    sys.exit("Please specify dev file and selected sentiment segments file")

dev_file = sys.argv[1]
sent_file = sys.argv[2]
out_sentiment = sent_file + ".dev"
outf = open(out_sentiment,'w')
#outf.write("doc_id\tframe_id\tframe_type\tsituation_type\tpred_seg_id\tpred_segment_text\tplace_id\tconf_score\tconf\n")
outf.write("user_id\tdoc_id\tframe_id\tpred_seg_id\t\tentity_id\tentity_type\tentity_mention\tsituation_type\tplace_id\tpred_segment_text\n")

with open(dev_file,'r') as d, open(sent_file,'r') as s:
    devs = d.readlines()
    sents = s.readlines()

#docs = []
docs = {}
for i in range(1,len(devs)):
    dev_line=devs[i]
    fields = dev_line.strip().split('\t')
    doc = fields[0]
    print(fields)
    seg_id = fields[6]
    print(doc, seg_id)
    #docs.append(doc)
    #docs.append([doc,seg_id])
    docs[(doc,seg_id)] = 1

for j in range(1,len(sents)  ):
    sent_line=sents[j]
    fields = sent_line.strip().split('\t')
    sent_doc = fields[1]
    sent_seg = fields[3]
    #sent_doc = sent_line.strip().split('\t')[0]
    if (sent_doc, sent_seg) in docs:
        print("Found doc_id and seg_id in dev set", sent_doc, sent_seg)
        outf.write(sent_line)
    else:
        print("Didn\'t find this doc_id and seg_id in the dev set. Excluding ", sent_doc, sent_seg)



