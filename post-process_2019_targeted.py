# Make final predictions, including source and intensity, for targeted systems
# Takes in predicted file (pasted with the fields from sent select)
# Outputs the format that we need for the scorer

import sys
import os
#from SEC_2019_utils import read_entity_dict_list

if len(sys.argv) < 4:
    sys.exit("Please specify an lstm output prediction file, output directory, and system name")
# TODO can specify thresholds for intensities/sources if needed
# TODO fields for targeted/untargeted (so we know whether to output the entity) or run separately and then combine?
# TODO en/es?
    
lstm_predictions = sys.argv[1]
out_dir = sys.argv[2]
system_name = sys.argv[3]

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

# store final predictions, indexed by user id, doc id, seg id, and frame id. Stores the entity and sentiment for that.
predictions_dict = {}


for i in range(1,len(predictions)):
    line = predictions[i].strip()
    fields = line.split('\t')
    user_id = fields[0]
    doc_id = fields[1]
    frame_id = fields[2]  # target_id?
    seg_id = fields[3]
    entity_id = fields[4]
    entity_type = fields[5]
    entity_mention = fields[6]
    seg_text = fields[10]
    sent_label = fields[11] 
    sent_probability = fields[12] # convert to float
    
    #if sent_label == "neutral":
    #    print("Neutral label")
    #    continue
    
    if not (user_id, doc_id, frame_id, seg_id) in predictions_dict:
        predictions_dict[(user_id, doc_id, frame_id, seg_id)] = []
    predictions_dict[(user_id, doc_id, frame_id, seg_id)].append([entity_id,entity_type,entity_mention,sent_label,sent_probability,seg_text])
    

# Now go through the predictions to consolidate them
    
for (user_id, doc_id, frame_id, seg_id) in predictions_dict:
    source = ""
    target = ""
    sent_value = 0.0
    final_label = ""
    final_probability = 0.0
    source_index = 0
    target_index = 0
    for predictions in predictions_dict[(user_id, doc_id, frame_id, seg_id)]:
        # There should be at most one targeted prediction for each user_id/doc_id/frame_id/seg_id combination
        entity_id = predictions[0]
        entity_type = predictions[1]
        entity_mention = predictions[2]
        sent_label = predictions[3]
        sent_probability = predictions[4]
        seg_text = predictions[5]
        print("Segment text:", seg_text)
        # TODO if multiple targets find the max probability
        
        if entity_mention != "none" and "Ent" in entity_id and sent_label != "neutral":
            print("Found target entity", entity_id, entity_mention, sent_label, sent_probability)
            if float(sent_probability) > final_probability:
                target = entity_id
                final_label = sent_label
                final_probability = float(sent_probability)
                target_index = seg_text.index(entity_mention)
            # TODO removing source predictions from targeted system, since it doesn't seem to work.
            #else:
            #    print("A target entity with lower probability. Checking if it could be source.")
            #    if entity_mention != "none" and "Ent" in entity_id and entity_type == "PER":
            #        print("Found potential source entity", entity_id, entity_mention, sent_label)
            #        source = entity_id
        # TODO removing since it doesn't seem to work. # No difference because the target is wrong
        elif entity_mention != "none" and "Ent" in entity_id and entity_type == "PER" and sent_label == "neutral":
            print("Found potential source entity", entity_id, entity_mention, sent_label)
            source = entity_id
            # TODO check if beginning or end of sentence
            source_index = seg_text.index(entity_mention)
    
    print("Source:", source, "Target:", target, "Source index:", source_index, "Target index:", target_index, "Sentiment:", final_label, "Probability:", sent_probability)
    
    if final_label == "neutral" or target == "":
        print("No targeted sentiment")
        continue
    
    if source_index > target_index:
        print("Source appears after the target. Unlikely to be a source") # TODO will hold for Spanish?
        source = ""
        
    print("We have targeted sentiment with source: ", source, "and target: ", target)
    print("Finalizing source and intensity.")
    
    # Process sources. Initialize the source values this way.
    if "SN" in doc_id:
        source = "author"
        print("Source is author")
    elif "DF" in doc_id and source == "":
        source = "author"
        print("Source is author")
        #if "Ent" in entity_id and entity_type == "PER":
        #    # TODO assuming for targeted we'd know that this entity is a target and we can check against it
        #    print("Found this potential source for DF:", entity_id, entity_type, entity_mention)
         #   source = entity_id
    elif "NW" in doc_id and source == "":
        source = "other"
        print("Source is other")
        #if "Ent" in entity_id and entity_type == "PER":
        #    print("Found this potential source for NW:", entity_id, entity_type, entity_mention)
        #    source = entity_id
            

    # Process intensities
    # TODO adjust values for targeted predictions?
    sent_probability = final_probability
    
    if sent_probability >= 0.9 and final_label == "negative": # TOD0 0.95?
        sent_value = -3.0
        emo1fear = 1
        emo2anger = 1
    elif sent_probability < 0.9 and sent_probability >= 0.8 and final_label == "negative":
        sent_value= -2.5
        emo1fear = 1
        emo2anger = 1
    elif sent_probability < 0.8 and sent_probability >= 0.7 and final_label == "negative":
        sent_value= -2.0
        emo1fear = 0
        emo2anger = 0
    elif sent_probability < 0.7 and sent_probability >= 0.6 and final_label == "negative":
        sent_value = -1.5
        emo1fear = 0
        emo2anger = 0
    elif sent_probability < 0.6 and sent_probability >= 0.5 and final_label == "negative":
        sent_value = -1.0
        emo1fear = 0
        emo2anger = 0
    elif sent_probability < 0.5 and final_label == "negative":
        sent_value = -0.5
        emo1fear = 0
        emo2anger = 0
    
    # TODO may need to adjust the values for positive since they have lower confidences
    if sent_probability >= 0.95 and final_label == "positive":
        sent_value = 3.0
        emo3joy = 1
    elif sent_probability < 0.95 and sent_probability >= 0.8 and final_label == "positive":
        sent_value= 2.5
        emo3joy = 1
    elif sent_probability < 0.8 and sent_probability >= 0.7 and final_label == "positive":
        sent_value= 2.0
        emo3joy = 1
    elif sent_probability < 0.7 and sent_probability >= 0.6 and final_label == "positive":
        sent_value = 1.5
        emo3joy = 0
    elif sent_probability < 0.6 and sent_probability >= 0.5 and final_label == "positive":
        sent_value = 1.0
        emo3joy = 0
    elif sent_probability < 0.5 and final_label == "positive":
        sent_value = 0.5
        emo3joy = 0
        
    
    print("Sent_probability:", sent_probability, "Sent_value:", sent_value, "Seg_text:", seg_text)
    
    of.write(system_name + "\t" + doc_id + "\t" + str(sent_value) + "\t" + str(emo1fear) + "\t" + str(emo2anger) + "\t" + str(emo3joy) + 
             "\t" + source + "\t" + target + "\t" + seg_id + "\n")
    
    
    # Fields: <system_name> <doc_id> <sentiment_value> <emo1> <emo2> <emo3> <source> <target> <seg_id>
    

# Output in required SEC test format