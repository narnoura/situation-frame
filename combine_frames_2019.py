# Combines data from training file and frame file for easier viewing of sentiment annotations
# Uses the 2019 sentiment frame annotation
# towards frames
# Run like this: python combine_frames.py <training_file> <frame_file> <segment_file>

import json
import sys
import os
import codecs
from collections import defaultdict

if len(sys.argv)<4:
    sys.exit("No input files specified. Exiting")
training_file = sys.argv[1]
frame_file = sys.argv[2]
segment_file = sys.argv[3]

frames_dict = {}
segments_dict = {}

with open(training_file,'r') as tr, open(frame_file,'r') as fr, codecs.open(segment_file,'r','utf-8') as se:
    train = tr.readlines()
    frame = fr.readlines()
    segment = se.readlines()

for s in range(0,len(segment)):
    (doc_id,segment_id,segment_text) = segment[s].strip().split("\t")
    doc_id = doc_id.replace(".ltf.xml","")
    segments_dict[doc_id,segment_id] = segment_text

for i in range(1,len(frame)):
    #(user_id, doc_id, frame_id, frame_type, situation_type, place_id, proxy_status, need_status, urgency_status, res_status, rep_by, res_by, desc) = frame[i].strip().split("\t")
    (doc_id, frame_id, frame_type, situation_type, place_id) = frame[i].strip().split("\t")
    frames_dict[frame_id] = {}
    frames_dict[frame_id]["Situation"] = situation_type
    frames_dict[frame_id]["Place"] = place_id
    frames_dict[frame_id]["DocumentID"] = doc_id
    frames_dict[frame_id]["FrameType"] = frame_type
    #frames_dict[frame_id]["ReportedBy"] = rep_by
    #frames_dict[frame_id]["ResolvedBy"] = res_by

out_frame = frame_file + "_sentiment"
outf = codecs.open(out_frame,'w','utf-8')
out_train = training_file + "_frame_type"
outt = codecs.open(out_train,'w','utf-8')
outf.write("doc_id\tframe_id\tframe_type\tsituation_type\tsentiment\temotion\tseg_id\tsegment_text\tplace_id\n")
outt.write("doc_id\tseg_id\tsentiment\temotion\tframe_id\tsituation_type\tentity_id\tsegment_text\tplace_id\n")

for j in range(1,len(train)):
    (doc_id, seg_id, sent_class, emo_class, frame_id, entity_id) = train[j].strip().split("\t")
    #(user_id, doc_id, sent_value, sent_class, emo_class, source, target, seg_id = train[j].strip().split("\t")
    if frame_id in frames_dict:
    # if target in frames_dict:
    # elif target in entity_dict:
        frames_dict[frame_id]["Sentiment"] = sent_class
        frames_dict[frame_id]["Emotion"] = emo_class
        frames_dict[frame_id]["Segment"] = seg_id
        frames_dict[frame_id]["SegmentText"] = segments_dict[doc_id,seg_id]
        outt.write(frames_dict[frame_id]["DocumentID"] + "\t" +
                        seg_id + "\t" +
                        sent_class + "\t" +
                        emo_class + "\t" +
                        frame_id + "\t" +
                        frames_dict[frame_id]["Situation"] + "\t" +
                        entity_id + "\t" +
                        segments_dict[doc_id,seg_id] + "\t" +
                        frames_dict[frame_id]["Place"] + "\n"
                    )
    elif frame_id == "none":
        outt.write(doc_id + "\t" +
                   seg_id + "\t" +
                   sent_class + "\t" +
                   emo_class + "\t" +
                   frame_id + "\t" +
                   "none" + "\t" +
                   entity_id + "\t" +
                   segments_dict[doc_id,seg_id] + "\t" +
                   "none" + "\n")
    else:
        sys.exit("Error: Missing frame " + frame_id + "Not in frames dic")


for frame_id in frames_dict:
    # BTW, this will only output one sentiment per frame, which is not always the case
    sentiment = ""
    emotion = ""
    segment = ""
    segment_text = ""
    if "Sentiment" in frames_dict[frame_id]:
        sentiment = frames_dict[frame_id]["Sentiment"]
    else:
        sentiment = "none"
    if "Emotion" in frames_dict[frame_id]:
        emotion = frames_dict[frame_id]["Emotion"]
    else:
        emotion = "none"
    if "Segment" in frames_dict[frame_id]:
        segment = frames_dict[frame_id]["Segment"]
        segment_text = frames_dict[frame_id]["SegmentText"]
    else:
        segment = "none"
        segment_text = "none"
    outf.write(frames_dict[frame_id]["DocumentID"] + "\t" +
               frame_id + "\t" +
               frames_dict[frame_id]["FrameType"] + "\t" +
               frames_dict[frame_id]["Situation"]  + "\t" +
               sentiment + "\t" +
               emotion + "\t" +
               segment + "\t" +
               segment_text + "\t" +
               frames_dict[frame_id]["Place"] + "\n"
               )
outf.close()
outt.close()
