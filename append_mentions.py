# Appends entity mentions to targeted entity training/test data

import sys
import os
from SEC_2019_utils import read_entity_dict, read_cmu_tweets

if len(sys.argv) < 4:
    sys.exit('Please specify a SEC-2019 training/dev/test file with entity targets, an entity mention file and a cmu json.txt file')
    
train_file = sys.argv[1]
entity_file = sys.argv[2]
cmu_file = sys.argv[3]
out_file = train_file + '.with_target_mentions.txt'

with open(train_file,'r') as tf:
    train_lines = tf.readlines()


of = open(out_file,'w')
header = train_lines[0].strip()
of.write(header + "\ttarget_entity_type\ttarget_mention_text\n")
#of.write("doc_id\tsentiment_value\tpolarity\temotion_value\tsource\ttarget\tsegment\tframe_type\tissue_need_type\tplace_id\ttext\ttarget_entity_type\ttarget_mention_text\n")
    
# Collect entities in dict
entity_dict = read_entity_dict(entity_file)

# Get cmu frames for tweets
tweets = read_cmu_tweets(cmu_file)

# Append to training data
for i in range(1,len(train_lines)):
    line = train_lines[i].strip()
    fields = line.split('\t')
    doc_id = fields[0]
    target_entity_id = fields[5]
    seg_id = fields[6]
    text = fields[len(fields)-1]
    if not (doc_id,target_entity_id,seg_id) in entity_dict:
        print('Didn\'t find this entity mention in the segment ', target_entity_id, doc_id, seg_id, text)
        # The entity is mentioned in another segment
    else:
        mention_text = entity_dict[doc_id,target_entity_id,seg_id]['mention_text']
        entity_type = entity_dict[doc_id,target_entity_id,seg_id]['entity_type']
        start_char = entity_dict[doc_id,target_entity_id,seg_id]['start_char']
        end_char = entity_dict[doc_id,target_entity_id,seg_id]['end_char']
        if '__' in mention_text: # this is a tweet
            print('found entity corresponding to a tweet. Searching in cmu tweets.')
            if (doc_id,seg_id) in tweets:
                print('found the tweet')
                text = tweets[(doc_id,seg_id)]
                print('tweet text:', text, 'start char:', start_char, 'end char:', end_char)
                start_char = int(start_char)
                end_char = int(end_char)+1
                mention_text = text[start_char:end_char]
                print('mention text:', mention_text)
        print("target entity id, type, text:", target_entity_id, entity_type, mention_text)
        of.write(line + '\t' + entity_type + '\t' + mention_text + '\n')
        

    

    
    
    
