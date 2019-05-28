# Simple evaluation of situation frames based on correctly retrieved pairs, with partial credit for incorrectly identified segments
# Run like this: pyhton simple_eval_frames.py <lstm-out.eval_new gold.eval_new>

import sys

if len(sys.argv) < 3:
    sys.exit("Please specify a prediction file and gold file")
    
pred_file = sys.argv[1]
gold_file = sys.argv[2]
pf = open(pred_file, 'r')
gf = open(gold_file, 'r')

gold_pairs={} # store the different user ids
predicted_pairs={} 
gold_pairs_partial={}
predicted_pairs_partial={}

# Read predictions
print('Storing predictions')
for line in pf:
    doc_id, frame_id, seg_id, sentiment = line.strip().split('\t')
    if sentiment == "neutral":
        continue
    if not (doc_id, frame_id, seg_id, sentiment) in predicted_pairs:
        predicted_pairs[doc_id, frame_id, seg_id, sentiment] = 1
        print('Added predicted pair', doc_id, frame_id, seg_id, sentiment)
    if not (doc_id, frame_id, sentiment) in predicted_pairs_partial:
        predicted_pairs_partial[doc_id, frame_id, sentiment] = 1
        
        
# Read gold
print('Storing gold pairs')
for line in gf:
    # NOTE there are no entity targets in this test data so we can safely assume for *this data* that they are all frames
    user_id, doc_id, intensity, sentiment, emotion, source, target, seg_id = line.strip().split('\t')
    if not (doc_id, target, seg_id, sentiment) in gold_pairs:
        gold_pairs[doc_id, target, seg_id, sentiment] = []
        print('Added gold pair pair', doc_id, target, seg_id, sentiment)
    if not user_id in gold_pairs[doc_id, target, seg_id, sentiment]:
        gold_pairs[doc_id, target, seg_id, sentiment].append(user_id)
        print('Appended user_id', user_id)
    if not (doc_id, target, sentiment) in gold_pairs_partial:
        gold_pairs_partial[doc_id, target, sentiment] = []
    if not user_id in gold_pairs_partial[doc_id, target, sentiment]:
        gold_pairs_partial[doc_id, target , sentiment].append(user_id)
    
print('Evaluating')

# For all classes
correct_strict=0
correct_partial=0
predicted_strict=0
predicted_partial=0
total_strict = 0
total_partial = 0

# For pos/neg
correct_strict_label={}
correct_partial_label={}
predicted_strict_label={}
predicted_partial_label={}
total_strict_label={}
total_partial_label={}

# Precision,recall,F-score
precision_strict = 0.0
recall_strict = 0.0

precision_strict_label = {}
recall_strict_label = {}
precision_partial_label = {}
recall_partial_label = {}

f_strict = 0.0
f_partial = 0.0
f_strict_label = {}
f_partial_label = {}

# Get total correct, for recall

# Strict measures
for gold_pair in gold_pairs:
    print('Gold pair:', gold_pair)
    label = gold_pair[3]
    user_ids = gold_pairs[gold_pair]
    total_strict += len(user_ids)
    print('Total strict:', total_strict)
    if not label in total_strict_label:
        total_strict_label[label] = 0
    if not label in correct_strict_label:
        correct_strict_label[label] = 0
    total_strict_label[label] += len(user_ids)
    if gold_pair in predicted_pairs:
        # found correct pair. Give x1 credit for one user_id and x2 credit for two user_ids
        print('found correct pair with number of user ids:', len(user_ids)) # note this means they agree. 
        correct_strict += len(user_ids)
        print('label:', label)
        correct_strict_label[label]+= len(user_ids)
    else:
        print('Didn`t find gold pair in predicted pairs')
        
        #TODO would this create recall > 1? no. and it wouldn't create precision > 1 because we count it twice if it's correct.
        #predicted_strict += len(user_ids)
        #predicted_strict_label[label] += len(user_ids)
  #  else:
        # If we miss it and it has 2 user ids, we get penalized for both for recall, but once for precision
   #     predicted_strict += 1
    #    predicted_strict_label[label] += 1
    
print('Number of labels:', len(total_strict_label))

# Partial measures measures
for gold_pair_partial in gold_pairs_partial:
    label = gold_pair_partial[2]
    user_ids_partial = gold_pairs_partial[gold_pair_partial]
    total_partial += len(user_ids)
    if not label in total_partial_label:
        total_partial_label[label] = 0
    if not label in correct_partial_label:
        correct_partial_label[label] = 0
    total_partial_label[label] += len(user_ids)
    if gold_pair_partial in predicted_pairs_partial:
        # found correct pair. Give x1 credit for one user_id and x2 credit for two user_ids
        print('found correct partial pair with number of user ids:', len(user_ids_partial)) # note this means they agree
        correct_partial += len(user_ids_partial)
        print('label:', label)
        correct_partial_label[label]+= len(user_ids_partial)
        
        # predicted_partial += len(user_ids_partial)
        #predicted_partial_label[label] += len(user_ids_partial)
    
    #else:
    
     #   predicted_partial += len(user_ids_partial)
      #  predicted_partial_label[label] += len(user_ids_partial)
        
# Get total predicted, for precision
for predicted_pair in predicted_pairs:
    label = predicted_pair[3]
    if not label in predicted_strict_label:
        predicted_strict_label[label] = 0
    if predicted_pair in gold_pairs:
        # To avoid getting precision > 1
        user_ids = gold_pairs[predicted_pair]
        predicted_strict += len(user_ids)
        predicted_strict_label[label] += len(user_ids)
    else:
        predicted_strict += 1
        predicted_strict_label[label] += 1
        
# Partial
for predicted_pair_partial in predicted_pairs_partial:
    label = predicted_pair_partial[2]
    if not label in predicted_partial_label:
        predicted_partial_label[label] = 0
    if predicted_pair_partial in gold_pairs_partial:
        # To avoid getting precision > 1
        user_ids_partial = gold_pairs_partial[predicted_pair_partial]
        predicted_partial += len(user_ids_partial)
        predicted_partial_label[label] += len(user_ids_partial)
    else:
        predicted_partial += 1
        predicted_partial_label[label] += 1


# Compute
recall_strict = float(correct_strict)/total_strict
recall_partial = float(correct_partial)/total_partial
precision_strict = float(correct_strict)/predicted_strict
precision_partial = float(correct_partial)/predicted_partial

if recall_strict != 0.0 and precision_strict != 0.0:
    f_strict = float(2*recall_strict*precision_strict)/(recall_strict + precision_strict)
else:
    f_strict = 0.0
    
if recall_partial != 0.0 and precision_partial != 0.0:
    f_partial= float(2*recall_partial*precision_partial)/(recall_partial + precision_partial)
else:
    f_partial = 0.0

for label in total_strict_label:
    if correct_strict_label[label] != 0.0:
        recall_strict_label[label] = float(correct_strict_label[label])/total_strict_label[label]
    else:
        recall_strict_label[label] = 0.0
    if predicted_strict_label[label] != 0.0:
        precision_strict_label[label] = float(correct_strict_label[label])/predicted_strict_label[label]
    else:
        precision_strict_label[label] = 1.0
    if recall_strict_label[label] != 0.0 and precision_strict_label[label] != 0.0:
        f_strict_label[label] = float(2*recall_strict_label[label]*precision_strict_label[label])/(recall_strict_label[label] + precision_strict_label[label])
    else:
        f_strict_label[label] = 0.0
        
    if correct_partial_label[label] != 0.0:
        recall_partial_label[label] = float(correct_partial_label[label])/total_partial_label[label]
    else:
        recall_partial_label[label] = 0.0
  
    if predicted_partial_label[label] != 0.0:
        precision_partial_label[label] = float(correct_partial_label[label])/predicted_partial_label[label]
    else:
        precision_partial_label[label] = 1.0
        
    if recall_partial_label[label] != 0.0 and precision_partial_label[label] != 0.0:
        f_partial_label[label] = float(2*recall_partial_label[label]*precision_partial_label[label])/(recall_partial_label[label] + precision_partial_label[label])
    else:
        f_partial_label[label] = 0.0
        

print("Strict score: ", "Precision:", precision_strict, " Recall:", recall_strict, " F-Measure:", f_strict)
print("Partial score: ", "Precision:", precision_partial, " Recall:", recall_partial, " F-Measure:", f_partial)

for label in total_strict_label:
    print(label, " strict score:", "Precision:", precision_strict_label[label], " Recall:", recall_strict_label[label], " F-Measure:", f_strict_label[label])
    print(label, " partial score:", "Precision:", precision_partial_label[label], " Recall:", recall_partial_label[label], " F-Measure:", f_partial_label[label] )

