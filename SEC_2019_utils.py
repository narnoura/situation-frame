import sys
import os

def read_entity_dict(entity_file):
    with open(entity_file, 'r') as ef:
        entities = ef.readlines()
    ef = open(entity_file, 'r')
    entity_dict = {}
    for i in range(1,len(entities)):
        line = entities[i].strip()
        fields = line.split('\t')
        doc_id = fields[0]
        entity_id = fields[1]
        entity_type = fields[2]
        seg_id = fields[3]
        start_char = fields[4]
        end_char = fields[5]
        mention_text = fields[6]
        if not (doc_id,entity_id,seg_id) in entity_dict:
            entity_dict[(doc_id,entity_id,seg_id)] = {}
        entity_dict[(doc_id,entity_id,seg_id)]['mention_text'] = mention_text
        entity_dict[(doc_id,entity_id,seg_id)]['entity_type'] =  entity_type
        entity_dict[(doc_id,entity_id,seg_id)]['start_char'] = start_char
        entity_dict[(doc_id,entity_id,seg_id)]['end_char'] = end_char
    return entity_dict

def read_entity_dict_list(entity_file):
    '''returns all mentions and ids in a doc_id,seg_is in a list'''
    with open(entity_file, 'r') as ef:
        entities = ef.readlines()
    ef = open(entity_file, 'r')
    entity_dict = {}
    for i in range(1,len(entities)):
        line = entities[i].strip()
        fields = line.split('\t')
        doc_id = fields[0]
        entity_id = fields[1]
        entity_type = fields[2]
        seg_id = fields[3]
        start_char = fields[4]
        end_char = fields[5]
        mention_text = fields[6]
        if not (doc_id,seg_id) in entity_dict:
            entity_dict[(doc_id,seg_id)] = []
        entity_dict[(doc_id,seg_id)].append([entity_id, entity_type, mention_text, start_char, end_char])
    return entity_dict

def read_cmu_tweets(cmu_file):
    ''' Returns text indexed by seg id and doc id in order to get the 
    right entity mentions for the tweets '''
    tweets = {}
    with open(cmu_file, 'r') as cf:
        frames = cf.readlines()
    for f in range(1,len(frames)):
        line=frames[f].strip()
        fields=line.split('\t')
        doc_id=fields[1] 
        seg_id=fields[5]
        text=fields[6]
        if seg_id != "segment-0":
            continue
        if not (doc_id,seg_id) in frames:
            tweets[(doc_id,seg_id)] = text
    return tweets

    