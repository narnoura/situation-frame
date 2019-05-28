# Make final predictions, including source and intensity
# Takes in predicted file (pasted with the fields from sent select)
# (this file: /proj/nlp/users/noura/LORELEI/SEC-2019/untargeted-exp/en/sec-all-euroTwitter-GLOVE)
# Outputs the format that we need for the scorer

import sys
import os
from SEC_2019_utils import read_entity_dict_list

if len(sys.argv) < 4:
    sys.exit("Please specify an lstm output prediction file, output directory, and system name")
# TODO can specify thresholds for intensities/sources if needed
# TODO fields for targeted/untargeted (so we know whether to output the entity) or run separately and then combine?
# TODO en/es?
    
lstm_predictions = sys.argv[1]
out_dir = sys.argv[2]
system_name = sys.argv[3]
targeted = 0
if len(sys.argv)==5:
    targeted = int(sys.argv[4])

#output_file = lstm_predictions + '.' + system_name + '.out.final'
output_file = os.path.join(out_dir, system_name + '.out')

# Fields: <system_name> <doc_id> <sentiment_value> <emo1> <emo2> <emo3> <source> <target> <seg_id>


fp = open(lstm_predictions,'r')
of = open(output_file,'w')
predictions = fp.readlines()

emo1fear = 0
emo2anger = 0
emo3joy = 0
source = ""
target = ""
sent_value = 0.0


for i in range(1,len(predictions)):
    line = predictions[i].strip()
    fields = line.split('\t')
    doc_id = fields[1]
    frame_id = fields[2]  # target_id?
    seg_id = fields[3]
    entity_id = fields[4]
    entity_type = fields[5]
    entity_mention = fields[6]
    seg_text = fields[10]
    sent_label = fields[11] 
    sent_probability = fields[12] # convert to float
    
    if sent_label == "neutral":
        print("Neutral label")
        continue

    # Process targets. If not targeted, predict frame as the target. Otherwise, check if the entity is none.
    # If the entity is not none, predict the entity as the target. But then what would be the source? Look in window? Have a final script to process these entities?
    
    target = frame_id # for now 
    
    # Process sources. Initialize the source values this way.
    if "SN" in doc_id:
        source = "author"
    elif "DF" in doc_id:
        source = "author" 
        #TODO trying Shabnam's way, remove below (b2). Should still keep predictions with the other way (b1) because the dev set is too small.
        if "Ent" in entity_id and entity_type == "PER":
            # TODO assuming for targeted we'd know that this entity is a target and we can check against it
            print("Found this potential source for DF:", entity_id, entity_type, entity_mention)
            source = entity_id
    elif "NW" in doc_id:
        source = "other" 
        if "Ent" in entity_id and entity_type == "PER":
            print("Found this potential source for NW:", entity_id, entity_type, entity_mention)
            source = entity_id
            

    # Process intensities
    # TODO if we use sec-semeval, we need to adjust these values since negative confidences will not be as high
    sent_probability = float(sent_probability)
    if sent_probability >= 0.9 and sent_label == "negative": # TOD0 0.95?
        sent_value = -3.0
        emo1fear = 1
        emo2anger = 1
    elif sent_probability < 0.9 and sent_probability >= 0.8 and sent_label == "negative":
        sent_value= -2.5
        emo1fear = 1
        emo2anger = 1
    elif sent_probability < 0.8 and sent_probability >= 0.7 and sent_label == "negative":
        sent_value= -2.0
        emo1fear = 0
        emo2anger = 0
    elif sent_probability < 0.7 and sent_probability >= 0.6 and sent_label == "negative":
        sent_value = -1.5
        emo1fear = 0
        emo2anger = 0
    elif sent_probability < 0.6 and sent_probability >= 0.5 and sent_label == "negative":
        sent_value = -1.0
        emo1fear = 0
        emo2anger = 0
    elif sent_probability < 0.5 and sent_label == "negative":
        sent_value = -0.5
        emo1fear = 0
        emo2anger = 0
    
    # TODO may need to adjust the values for positive since they have lower confidences
    if sent_probability >= 0.95 and sent_label == "positive":
        sent_value = 3.0
        emo3joy = 1
    elif sent_probability < 0.95 and sent_probability >= 0.8 and sent_label == "positive":
        sent_value= 2.5
        emo3joy = 1
    elif sent_probability < 0.8 and sent_probability >= 0.7 and sent_label == "positive":
        sent_value= 2.0
        emo3joy = 1
    elif sent_probability < 0.7 and sent_probability >= 0.6 and sent_label == "positive":
        sent_value = 1.5
        emo3joy = 0
    elif sent_probability < 0.6 and sent_probability >= 0.5 and sent_label == "positive":
        sent_value = 1.0
        emo3joy = 0
    elif sent_probability < 0.5 and sent_label == "positive":
        sent_value = 0.5
        emo3joy = 0
        
    
    print("Sent_probability:", sent_probability, "Sent_value:", sent_value, "Seg_text:", seg_text)
    
    of.write(system_name + "\t" + doc_id + "\t" + str(sent_value) + "\t" + str(emo1fear) + "\t" + str(emo2anger) + "\t" + str(emo3joy) + 
             "\t" + source + "\t" + target + "\t" + seg_id + "\n")
    
    
    # Fields: <system_name> <doc_id> <sentiment_value> <emo1> <emo2> <emo3> <source> <target> <seg_id>
    

# Output in required SEC test format