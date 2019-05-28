# Processes cmu frames for the format provided in SEC 2019, which has the gold frames annotation
# Takes in the concatenated frame tab files in order to match these frames with their frame ids (which are not provided by cmu)
# Changes frame types to match SEC annotation

import json
import sys
import os
import codecs
from pprint import pprint


def convert_type(cmu_frame):
    if cmu_frame == "Infrastructure":
        return "infra"
    elif cmu_frame == "Evacuation":
        return "evac"
    elif cmu_frame == "Shelter":
        return "shelter"
    elif cmu_frame == "Food Supply":
        return "food"
    elif cmu_frame == "Medical Assistance":
        return "med"
    elif cmu_frame == "Water Supply":
        return "water"
    elif cmu_frame == "Search_Rescue" or cmu_frame == "Search/Rescue":
        return "search"
    elif cmu_frame == "Utilities, Energy, or Sanitation":
        return "utils"
    elif cmu_frame == "Civil Unrest or Wide-spread Crime":
        return "crimeviolence"
    elif cmu_frame == "Terrorism or other Extreme Violence":
        return "terrorism"
    elif cmu_frame == "Regime Change":
        return "regimechange"
    else:
        #print "Invalid type ", cmu_frame
        return cmu_frame

if len(sys.argv)<2:
    sys.exit("No input json file specified. Exiting")
if len(sys.argv)<3:
    sys.exit("Please also specify a file containing all frame ids.")
cmu_file = sys.argv[1]
frame_file = sys.argv[2]

print("Reading this SF file:", cmu_file)
print("Reading this frame file:", frame_file)

#out_file = cmu_file + '.2.txt'
out_file = cmu_file + '.txt'
print("Writing to this file:", out_file)

with open(cmu_file,'r') as cmu:
    frames = json.load(cmu)
out = codecs.open(out_file,'w','utf-8')
#out.write("doc_id\tcmu_frame\tconf\tsegment_id\tkeywords\ttext\n")
out.write("user_id\tdoc_id\tframe_id\tframe_type\ttypeconf\tseg_id\ttext\tplace_id\tplace_mention\tframe_status\trelief\turgency\n")



# Get the frame ids from the original file
fr = open(frame_file,'r')
frames_dict = {}
frames_dict_nodesc = {} # for frames where we don't have the anchoring
for line in fr:
    #try:
    #    user_id, doc_id, frame_id, frame_type, situation_type, place_id, proxy_status, frame_status, description = line.strip().split("\t")
    #except:
    #    print("err:",line)
    # need and issues have different fields because needs will have the gold info
    fields = line.strip().split("\t")
    user_id = fields[0]
    doc_id = fields[1]
    frame_id = fields[2]
    frame_type = fields[3]
    situation_type = fields[4]
    place_id = fields[5]
    proxy_status = fields[6]
    frame_status = fields[7]
    # TODO then need specific fields (urgency_status, resolution_status, reported_by, and resolved_by)
    description = fields[len(fields)-1]   
    if user_id == "user_id" and doc_id == "doc_id":
        continue
    
    if not (user_id, doc_id, situation_type, place_id, frame_status, description) in frames_dict:
        frames_dict[(user_id, doc_id, situation_type, place_id, frame_status, description)] = frame_id
    else:
        print("found duplicate frame:", (user_id, doc_id, situation_type, place_id, frame_status, description))
          
    # if text and segment id is not null
    if not (doc_id, situation_type) in frames_dict_nodesc:
        frames_dict_nodesc[(doc_id, situation_type)] = []
    frames_dict_nodesc[(doc_id, situation_type)].append([user_id,frame_id,place_id,frame_status,description])
    print("Appended this nodescription frame ", doc_id, situation_type, user_id, frame_id, place_id, frame_status,description)
    #else:
    #    print("found duplicate no description frame:", (user_id, doc_id, situation_type, place_id, frame_status, frame_id))
    #    print("the frame id:", frames_dict_nodesc[(user_id, doc_id, situation_type, place_id, frame_status)])     
    #frames_dict[doc_id][frame_id] = {}
    #frames_dict[doc_id][frame_id]["Situation"] = situation_type
    #frames_dict[doc_id][frame_id]["Place"] = place_id
    #frames_dict[doc_id][frame_id]["FrameType"] = frame_type


# Now read the json file
doc_id = ""  
type = ""
typeconf = 0.0
sec_type = ""
text = ""
seg_id = ""
text_segment = "none"
# place mention
place_men_start = "none"
place_men_end = "none"
place_men_type = "none"
place_men = "none"
place_id = "none" # TODO check if this is mention or entity id
source = "none"  # TODO what's this?

frame_id = "none"
frame_status = "none"
frame_type = "none"
relief = "none"
urgency = "none"
keyword = "none"

#keyword_txt = "NA" TODO later
#start = "NA"
#end = "NA"
#keywords = "NA"

print("Number of frames, or len(frames), is ", len(frames) )
for i in range(0,len(frames)):
    elem = frames[i]
    doc_id = elem["DocumentID"]
    sf_type = elem["Type"]
    typeconf = elem["TypeConfidence"]
    sec_type = convert_type(sf_type)
    text = elem["Text"]   # the text description. In the predicted frames, it's the actual segment.
    print("Text:", text)
    if 'TextSegment' in elem:
        text_segment = elem["TextSegment"] # the full segment
    else:
        text_segment = "none" # (why?)
    #text_segment = text_segment.replace("|||", "")  # TODO should we? or later better
    text_segment = text_segment.replace("\n", " ")
    if "SegmentID" in elem:
        seg_id = elem["SegmentID"]
    elif "Justification_ID" in elem:
        print("Found justification ID", seg_id)
        seg_id = elem["Justification_ID"]
    if seg_id == None:
        seg_id = "none"
    # place elem
    if "PlaceMention" in elem:
        place_elem = elem["PlaceMention"]
        if "End" in place_elem:
            place_men_end = place_elem["End"]
        else:
            place_men_end = "none"
        if "EntityType" in place_elem:
            place_men_type = place_elem["EntityType"]
        else:
            place_men_type = "none"
        if "End" in place_elem:
            place_men_place = place_elem["Place"]
        else:
            place_men_place = "none"
        if "Start" in place_elem:
            place_men_start = place_elem["Start"]
        else:
            place_men_Start = "none"
    if "Place_KB_ID" in elem:
        place_id = elem["Place_KB_ID"]
    if place_id == "":
        place_id = "none"
    user_id = elem["Source"]
    # status elem
    if "Status" in elem:
        status_elem = elem["Status"]
        if "Need" in status_elem:
            frame_type = "Need"
            frame_status = status_elem["Need"]
        elif "Issue" in status_elem:
            frame_type = "Issue"
            frame_status = status_elem["Issue"]
        if "Urgent" in status_elem:
            urgency = str(status_elem["Urgent"])
        else:
            urgency = "none"
        if "Relief" in status_elem:
            relief = status_elem["Relief"]
        else:
            relief = "none"
        #out.write("doc_id\tcmu_frame\tconf\tsegment_id\tkeywords\ttext\n")
    if "Keyword" in elem:
        keyword = elem["Keyword"]
    print(doc_id, seg_id)
    # Get frame id
    if (user_id, doc_id, sec_type, place_id, frame_status, text) in frames_dict:
        frame_id = frames_dict[(user_id, doc_id, sec_type, place_id, frame_status, text)]
        print("found frame", frame_id)
    elif (doc_id, sec_type) in frames_dict_nodesc:
        frame_ids = frames_dict_nodesc[(doc_id, sec_type)]
        print("found the predicted cmu frame in frames_dict_nodesc", "number of predicted segments:", len(frame_ids))
        for user_id,f,place_id,frame_status,description in frame_ids:
            try:
                out.write(user_id + "\t" + doc_id + "\t" + f + "\t" + sec_type + "\t" + str(typeconf) + "\t" + seg_id + "\t" + text + "\t" + place_id + "\t" + place_men + "\t" + frame_status + "\t" + relief + "\t" + urgency + "\n")
            except:
                print("error ids:", doc_id, seg_id)
        continue
    else:
        print("did not find frame id for", (user_id, doc_id, sec_type, place_id, frame_status, text))
        frame_id = "not_found"
        continue
    try:
        out.write(user_id + "\t" + doc_id + "\t" + frame_id + "\t" + sec_type + "\t" + str(typeconf) + "\t" + seg_id + "\t" + text_segment + "\t" + place_id + "\t" + place_men + "\t" + frame_status + "\t" + relief + "\t" + urgency + "\n")
    except:
        print("error ids:", doc_id, seg_id)
        

   # Efsun
   # out.write(text + "\n")
out.close()
