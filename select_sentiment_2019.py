 # Select segments for sentiment prediction within window for SEC-2019 eval
# In addition to including frame segments within the window, if any entity or entity mention is present in the window,
# it will be appended and used to create a new data point.
# Inputs: ltf file, cmu file, and entity mention file, and window

# Given a list of frames with segments, select segments for sentiment analysis
# Each (frame id, segment-id) pair should be unique (not the case if we add entity ids and user ids)
# Run like this: python select_sentiment.py <SEC data> <consolidated frames file> <window> <entity_file>
#
# Look at neighboring segments in a given window, add them as segments for sentiment prediction
# For frames with NA (no CMU prediction), add all doc segments
# Optionally check using MPQA if they contain strongly subjective terms
#
# The more I look at the segments the more I think keywords and LDA might be helpful (can include
# in Tao system make it topic dependent or take in topic)


import sys
import os
from SEC_2019_utils import read_entity_dict_list

if len(sys.argv)<5:
    sys.exit("Please specify all arguments: <SEC data file> <consolidated frame file> <search window> <entity file>")

segment_file = sys.argv[1]
cons_frame = sys.argv[2]
window = sys.argv[3]
entity_file = sys.argv[4]
#use_sentiment_words = 0

segments_dict={}
frames_dict={}

with open (segment_file,'r') as se, open(cons_frame, 'r') as cf:
    segment = se.readlines()
    frame = cf.readlines()
    
entity_dict = read_entity_dict_list(entity_file)

out_sentiment = cons_frame + "_sent_select_"+window
outf = open(out_sentiment,'w')

#outf.write("doc_id\tframe_id\tframe_type\tsituation_type\tpred_seg_id\tpred_segment_text\tplace_id\tconf_score\tconf\n")
outf.write("user_id\tdoc_id\tframe_id\tpred_seg_id\t\tentity_id\tentity_type\tentity_mention\tsituation_type\tplace_id\tpred_segment_text\n")

for s in range(0,len(segment)):
    (doc_id,segment_id,segment_text) = segment[s].strip().split("\t")
    doc_id = doc_id.replace(".ltf.xml","")
    if not doc_id in segments_dict:
        segments_dict[doc_id]=[]
    segments_dict[doc_id].append(segment_text)

for f in range(1,len(frame)):
    line=frame[f].strip()
    fields=line.split('\t')
    user_id=fields[0]
    doc_id=fields[1]
    frame_id=fields[2]
    situation_type=fields[3]
    seg_id=fields[5]
    text=fields[6]
    place_id=fields[7]
    place_mention=fields[8]
    # predicted system: might not have all
  
    if seg_id == 'none':
        # Tweets that were deleted
        continue
    
    # TODO spanish frames with no description
    
    # have a predicted segment, look for sentiment around it

    # Process " ||| " segments
    if "|||" in seg_id:
        print("Found multiple segments in one")
        split_segs = seg_id.split("|||")
        #split_texts = text.split("|||") # what about tweets? won't be in this case because they are all single segments
        seg, first_id = split_segs[0].strip().split("-")
        first_id = int(first_id)
        seg, last_id = split_segs[len(split_segs)-1].strip().split("-")
        last_id = int(last_id)
        print("first id:", first_id, "last id", last_id)
        window = int(window)
        r1 = first_id - window
        r2 = last_id + window
        for j in range(r1,r2+1):
            if j < 0:
                continue
            try:
                seg_context = segments_dict[doc_id][j]
                seg_context_id = "segment-" + str(j)
  
                # Process entities
                if not (doc_id, seg_context_id) in entity_dict:
                    print('Didn\'t find any entities in this segment.')
                    outf.write(
                           user_id + "\t" +
                           doc_id + "\t" +
                           frame_id + "\t" +
                           seg_context_id + "\t"+
                           "none" + "\t" +
                           "none" + "\t" +
                           "none" + "\t" +
                           situation_type  + "\t" +
                           place_id + "\t" +
                           place_mention + "\t" +
                           seg_context + "\n"
                           )
                    
                else:
                    print("Found entities in this segment!")
                    for entity in entity_dict[(doc_id,seg_context_id)]:
                        entity_id = entity[0]
                        entity_type = entity[1]
                        entity_mention = entity[2]
                        if '__' in entity_mention:
                            print('found tweet mention')
                            start_char = entity[3]
                            end_char = entity[4]
                            print('start char:', start_char, 'end char:', end_char)
                            start_char = int(start_char)
                            end_char = int(end_char)+1
                            entity_mention = seg_context[start_char:end_char]
                            print('entity mention:', entity_mention)
                        print(entity_id, entity_type, entity_mention)
                        outf.write(
                                user_id + "\t" +
                                doc_id + "\t" +
                                frame_id + "\t" +
                                seg_context_id + "\t"+
                                entity_id + "\t" +
                                entity_type + "\t" +
                                entity_mention + "\t" +
                                situation_type  + "\t" +
                                place_id + "\t" +
                                place_mention + "\t" +
                                seg_context + "\n"
                                )
            except IndexError:
                seg_context = ""
                
    else:
        print("Single segment in one")
        seg,id = seg_id.split("-")
        id = int(id)
        window = int(window)
        seg_context = ""
        
        for j in range(-window,window+1):
            if (id+j) >= 0:
                try:
                    seg_context = segments_dict[doc_id][id+j]
                    seg_context_id = "segment-" + str(id+j)
                    # cmu tweets
                    if j == 0:
                        seg_context = text
  
                    # Process entities
                    if not (doc_id, seg_context_id) in entity_dict:
                        print('Didn\'t find any entities in this segment.')
                        outf.write(
                                user_id + "\t" +
                                doc_id + "\t" +
                                frame_id + "\t" +
                                seg_context_id + "\t"+
                                "none" + "\t" +
                                "none" + "\t" +
                                "none" + "\t" +
                                situation_type  + "\t" +
                                place_id + "\t" +
                                place_mention + "\t" +
                                seg_context + "\n"
                           )
                    else:
                        print("Found entities in this segment!")
                        for entity in entity_dict[(doc_id,seg_context_id)]:
                            entity_id = entity[0]
                            entity_type = entity[1]
                            entity_mention = entity[2]
                            print(entity_id, entity_type, entity_mention)
                            if '__' in entity_mention:
                                print('found tweet mention')
                                start_char = entity[3]
                                end_char = entity[4]
                                print('start char:', start_char, 'end char:', end_char)
                                start_char = int(start_char)
                                end_char = int(end_char)+1
                                entity_mention = seg_context[start_char:end_char]
                                print('entity mention:', entity_mention)
                            print(entity_id, entity_type, entity_mention)
                            outf.write(
                                user_id + "\t" +
                                doc_id + "\t" +
                                frame_id + "\t" +
                                seg_context_id + "\t"+
                                entity_id + "\t" +
                                entity_type + "\t" +
                                entity_mention + "\t" +
                                situation_type  + "\t" +
                                place_id + "\t" +
                                place_mention + "\t" +
                                seg_context + "\n"
                                )     
      
                except IndexError:
                    seg_context = ""
            else:
                seg_context = ""
        # Then write predictions to a similar file

