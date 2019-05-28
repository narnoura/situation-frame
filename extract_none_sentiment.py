# Takes pilot-2019 training file (from Brenda) and the ltf segments (all.ltf.lang.txt)
# and produces a training file with segments having none sentiment.
# Additionally separates the positive/negative data between segments with frame targets and segments with entity targets
# Finally, it also identifies the tweet segments (____), matches them with cmu (along with the frame sec type for none segments) 
# and replaces the downloaded tweets in the segment text field and the frame id in the sec type (need_issue_type) field,
# this is if we want to use the type or the keywords later on in the targeted system.


import sys


if len(sys.argv) < 4:
    sys.exit("Please specify a Pilot-2019 training file, a monolingual all.ltf.language.txt file, and a cmu .json.txt file containing frames")
    
train_file = sys.argv[1]
ltf_file = sys.argv[2]
cmu_file = sys.argv[3]

with open(train_file, 'r') as tf, open(ltf_file, 'r') as lf, open(cmu_file,'r') as cf:
    train = tf.readlines()
    ltf = lf.readlines()
    cmu = cf.readlines()
    
out_none = train_file + '.nosentiment'
out_all = train_file + '.all'  
out_frame_targets = train_file + '.frame.targets'
out_entity_targets = train_file + '.entity.targets'

fn = open(out_none,'w')
fa = open(out_all, 'w')
ft = open(out_frame_targets, 'w')
fe = open(out_entity_targets, 'w')
fn.write('doc_id\tsentiment_value\tpolarity\temotion_value\tsource\ttarget\tsegment\tframe_type\tissue_need_type\tplace_id\ttext\n')
fa.write('doc_id\tsentiment_value\tpolarity\temotion_value\tsource\ttarget\tsegment\tframe_type\tissue_need_type\tplace_id\ttext\n')
ft.write('doc_id\tsentiment_value\tpolarity\temotion_value\tsource\ttarget\tsegment\tframe_type\tissue_need_type\tplace_id\ttext\n')
fe.write('doc_id\tsentiment_value\tpolarity\temotion_value\tsource\ttarget\tsegment\tframe_type\tissue_need_type\tplace_id\ttext\n')


segments_dict_PN = {} # positive and negative segments
segments_dict_none= {} # neutral segments
segments_dict_cmu = {} # collect cmu segments

for c in range(1, len(cmu)):
    line = cmu[c]
    fields = line.strip().split('\t')
    doc_id = fields[1]
    seg_id = fields[5]
    seg_text = fields[6]
    frame_id = fields[2]
    sec_type = fields[3]
    segments_dict_cmu[doc_id, seg_id] = [seg_text, sec_type]
    

for i in range(1,len(train)):
    line = train[i]
    fields = line.strip().split('\t')
    doc_id = fields[0]
    seg_id = fields[6]
    segment_text = fields[10]
    if '___' in segment_text:
        print('Found hidden tweet segment', seg_id, doc_id, segment_text)
        print('Checking cmu')
        if (doc_id,seg_id) in segments_dict_cmu:
            print('Found it')
            segment_text = segments_dict_cmu[doc_id,seg_id][0]
            print('The segment text is:', segment_text)
            fields[10] = segment_text
            #print('Fields[10] is:', fields[10])
        else:
            print('Didn\'t find this PN tweet, it must have been deleted.')
    segments_dict_PN[doc_id,seg_id] = segment_text
    # TODO tweet/ empty segments. We will match them with CMU. If they are neutral or unrelated to the frame then I don't care.
    fa.write('\t'.join(fields) + '\n')
    #source = fields[4]
    target = fields[5]
    if 'Frame-' in target:
        #ft.write(line)
        ft.write('\t'.join(fields) + '\n')
    elif 'Ent-' in target:
        #fe.write(line)
        fe.write('\t'.join(fields) + '\n')
    else:
        print('Invalid target ', target)
    
for j in range(len(ltf)):
    line = ltf[j]
    doc_id, seg_id, text = line.strip().split('\t')
    doc_id = doc_id.replace(".ltf.xml","")
    if (doc_id,seg_id) not in segments_dict_PN:
        print('Found neutral/none segment:', doc_id, seg_id, text)
        if '___' in text:
            print('Found hidden neutral/none tweet segment', seg_id, doc_id, text)
            print('Checking cmu')
            if (doc_id,seg_id) in segments_dict_cmu:
                print('Found it')
                text = segments_dict_cmu[doc_id,seg_id][0]
                print('The segment text is:', text)
            else: 
                print('Didn\'t find this none/neutral tweet, it must have been deleted')
        # Get frame id and type
        #if (doc_id,seg_id) in segments_dict_cmu:
        #    sec_type = segments_dict_cmu[doc_id,seg_id][1]
        #    print('Found situation type for this frame:', doc_id, seg_id, sec_type, text)
        #else:
        #    sec_type = "none"
        #fn.write(doc_id + '\tnone\tnone\tnone\tnone\tnone\t' + seg_id + '\tnone\t' + sec_type + '\tnone\t' + text + '\n')
        #fa.write(doc_id + '\tnone\tnone\tnone\tnone\tnone\t' + seg_id + '\tnone\t' + sec_type + '\t none\t'  + text + '\n')
        fn.write(doc_id + '\tnone\tnone\tnone\tnone\tnone\t' + seg_id + '\tnone\tnone\tnone\t' + text + '\n')
        fa.write(doc_id + '\tnone\tnone\tnone\tnone\tnone\t' + seg_id + '\tnone\tnone\tnone\t' + text + '\n')
    else:
        print('This segment has positive/negative sentiment:', doc_id, seg_id, segments_dict_PN[doc_id,seg_id])
        
    