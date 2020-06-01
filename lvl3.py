# HTML Content Checker
# Purpose: To check if HTML DOM Tree structure is any different
# How?
# Go 6 levels up, find tree structure
# Compare to previously stored tree structure
# TO DO:
# Find fn showing how different trees are:
# 1. (Level+1)^2 + some tag shit
# Input: Parsing Xpath

import logging
import datetime
import json
import glob
from pyquery import PyQuery as pq
import os

def count_fn():
    count_fn.count += 1
    return count_fn.count
count_fn.count = 0

def get_tree(ele, tree_list):
    master_tree_list = []
    for i in ele:
        #print(i.tag)
        queue = []
        queue.append([i,0])
        while queue:
            pop_ele, depth = queue.pop(0)
            #print(pop_ele.tag)
            tree_list.append([pop_ele.tag,pq(pop_ele).attr('class'), pq(pop_ele).attr('id'), count_fn(), depth])
            for j in pq(pop_ele).children():
                queue.append([j,depth+1])
        master_tree_list.extend(tree_list)
    return master_tree_list

def get_prev_tree_list():
    tree_list = glob.glob('treelist*')
    #print('here in fn')
    #print(tree_list)
    if (len(tree_list) < 2):
        print('never mind')
        return
    tree_list_sorted = sorted(tree_list, key=os.path.getmtime, reverse=True)
    ref = tree_list_sorted[0]
    f = open(ref)
    ref_obj = json.loads(f.read())
    #print(ref_obj['tree_data'])
    return ref_obj['tree_data']


def html_check(base_url, pq_obj):
    logger = logging.getLogger(__name__)
    count_fn().count = 0
    prev_tree_list = get_prev_tree_list()
    print(type(prev_tree_list))
    tree_list = get_tree(pq_obj.children(), [])
    write_time = datetime.datetime.now()
    json_dict = {'mod_time':write_time.strftime("%d%b%Y%H_%M_%S_%f"), 'tree_data':tree_list}
    f = open(f'treelist{write_time.strftime("%d%b%Y%H_%M_%S_%f")}.json', 'w')
    json.dump(json_dict,f)
    #TODO: DECIDE FN
    multipliers = {i:2**-i for i in range(6)}
    new_score = 0
    prev_score = 0
    diff = 0
    for i, j in zip(tree_list, prev_tree_list):
        if(i!=j):
            logger.warning(f'Base URL:{base_url}. Mismatch: >{i}\n<{j}')
            diff = 1
    if(diff==0):
        print('Not Different!')
