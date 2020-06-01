from pyquery import PyQuery as pq
from pprint import pprint
import hashlib
import uuid
from lxml.etree import _Element as ele
import pickle
import json
import datetime
import glob
import os
import logging
import re
from browhat import nice

def count_fn():
    count_fn.count += 1
    return count_fn.count
count_fn.count = 0

def get_paths(pq_obj, path_list):
    ret_paths = []
    curr_path = path_list.copy()
    curr_path.extend(pq_obj)
    for i in pq_obj.children():
        ret_obj = get_paths(pq(i), curr_path)
        if(not isinstance(ret_obj[0], list)):
            ret_paths.append(pq(ret_obj))

        else:
            for i in ret_obj:
                ret_paths.append(i)
    if(not pq_obj.children()):
        return curr_path
    #print(ret_paths)
    return ret_paths

def get_hashes(pq_obj, lis):
    errhashes = []
    warnhashes = []
    paths = get_paths(pq_obj, lis)
    pprint(paths)
    for i in paths:
        error_tags = []
        warning_tags = []
        for j in i:
            if(j.tag not in ['option', 'li']):
                error_tags.append([j.tag, pq(j).attr('class'), pq(j).attr('id'), count_fn()])
            else:
                warning_tags.append([j.tag, pq(j).attr('class'), pq(j).attr('id'), count_fn()])
        print('error tags:', str(error_tags))
        print('warning tags:', str(warning_tags))
        errdump_obj = pickle.dumps(error_tags)
        warndump_obj = pickle.dumps(warning_tags)
        warnhashes.append(hashlib.sha1(warndump_obj).hexdigest())
        errhashes.append(hashlib.sha1(errdump_obj).hexdigest())
    #pprint(paths)
    return tuple([sorted(warnhashes), sorted(errhashes)])


def write_hashfile(pq_obj, lis, base_url):
    rand_id = uuid.uuid4()
    f1 = open('htmlerr'+str(rand_id), 'w')
    f2 = open('htmlwarn'+str(rand_id), 'w')
    hash_tup = get_hashes(pq_obj, lis)
    mod_time = datetime.datetime.now().strftime('%d-%b-%Y (%H:%M:%S.%f)')
    log_dict_err = {'Modified Time':mod_time, 'Hashes':hash_tup[0], 'Base URL':base_url}
    log_dict_warn = {'Modified Time':mod_time, 'Hashes':hash_tup[1], 'Base URL':base_url}
    json.dump(log_dict_err, f1, indent=4)
    json.dump(log_dict_warn, f2, indent=4)
    f1.close()
    f2.close()

def write_and_compare(pq_obj,lis,base_url):
    logging.basicConfig(filename="ramyasaidso.txt",
                        filemode='a',
                        format='%(asctime)s %(levelname)s-%(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    write_hashfile(pq_obj, lis, base_url)
    err_list = glob.glob('htmlerr*')
    if(len(err_list)<2):
        print('never mind')
        return
    err_list_sorted = sorted(err_list, key=os.path.getmtime, reverse=True)
    warn_list = glob.glob('htmlwarn*')
    if (len(warn_list) < 2):
        print('never mind')
        return
    warn_list_sorted = sorted(warn_list, key=os.path.getmtime, reverse=True)
    ref_err = err_list_sorted[1]
    new_err = err_list_sorted[0]
    ref_warn = warn_list_sorted[1]
    new_warn = warn_list_sorted[0]
    ref_err_fobj = open(ref_err)
    new_err_fobj = open(new_err)
    ref_warn_fobj = open(ref_warn)
    new_warn_fobj = open(new_warn)
    ref_err_list = json.load(ref_err_fobj)
    print(ref_err_list['Hashes'])
    new_err_list = json.load(new_err_fobj)
    ref_warn_list = json.load(ref_warn_fobj)
    new_warn_list = json.load(new_warn_fobj)
    print(ref_err_list['Hashes']==new_err_list['Hashes'])
    if(ref_err_list['Hashes']==new_err_list['Hashes']):
        print(f'{base_url} : FORMAT OK')
        logging.info(base_url+' : FORMAT OK')
    else:
        logging.error(base_url+' : CODE CHANGED REQUIRED')
    if(ref_warn_list['Hashes']==new_warn_list['Hashes']):
        logging.info(f'{base_url} : LIST CONTENT OK')
    else:
        logging.warning(f'{base_url} : LIST CONTENT CHANGED')



if __name__=='__main__':
    nice()