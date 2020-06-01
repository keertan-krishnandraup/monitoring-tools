import json
import logging
import requests
import datetime
import glob
from pyquery import PyQuery as pq
import os


logging.basicConfig(filename='flask_log.txt',filemode='w',level=logging.DEBUG)
def master_check(base_url, source_name, method, MAX_RETRIES, meta=None, proxy=None, proxy_pool = None):
    logger = logging.getLogger(__name__)
    print('here')
    logger.info(f'Source Name:{source_name}\nBase URL:{base_url}\n')
    #To store blocked proxies
    blocked = []
    curr_proxy = proxy #TODO Change to master proxy server IP
    resp1, blocked = master_level1(base_url, method, meta,MAX_RETRIES, curr_proxy, blocked, proxy_pool)
    yield resp1
    item = yield
    conn, doc = item[0], item[1]
    if(conn is None or doc is None):
        logger.warning('Connection or Document is None')
        logger.warning('Skipping level 2 check')
        yield 0
    else:
        format_flag = level2(base_url, conn, doc)
        if(format_flag==1):
            lev2_retry = 0
            logger.warning('Some fields returned empty from level 2 check.')
            logger.info('Reinitiating w/ diff proxy')
            blocked.append(curr_proxy)
            for i in proxy_pool:
                if(i not in blocked):
                    curr_proxy=i
            resp1, blocked = master_level1(base_url, method,MAX_RETRIES, meta, curr_proxy, blocked)
            if(resp1!=200):
                logger.warning(f'Non 200 response code. Response Code:{resp1}')
            else:
                while(lev2_retry<3 and format_flag==1):
                    lev2_retry+=1
                    format_flag = level2(base_url, conn, doc)
        yield format_flag
    item = yield
    if(item is None):
        logger.warning(f'Level 3 check being skipped')
        yield 0
    else:
        pq_str  = item
        flag = level3(base_url, pq_str)
        print(flag)
        yield flag


def master_level1(base_url, method, meta,MAX_RETRIES,  curr_proxy, blocked, proxy_pool):
    logger = logging.getLogger(__name__)
    retries = 0
    resp = level1(base_url, method, meta, curr_proxy, blocked)
    retries += 1
    # Retry Worthy response codes
    # TODO Find Response codes indicating retry worthy
    retry_worthy = [403]
    # TODO Find Response codes indicating block
    # Response Codes indicating certain block
    block_codes = []
    if (resp in block_codes):
        if (curr_proxy != None):
            blocked.append(curr_proxy)
        if(proxy_pool!=None):
            for i in proxy_pool:
                if (i not in blocked):
                    curr_proxy = i
            while (resp in block_codes and retries < MAX_RETRIES):
                resp = level1(base_url, method, meta, curr_proxy, blocked)
                retries += 1
    if (resp in retry_worthy):
        retries = 0
        while (resp in retry_worthy and retries < MAX_RETRIES):
            logger.info(f'Base URL:{base_url}.Retrying')
            resp = level1(base_url, method, meta, curr_proxy, blocked)
            retries += 1
    if (resp == 200):
        logger.info('Status 200 returned')
        logger.info('Level 1 check completed.')
        resp1 = 'Purfect'
    elif (resp == 1):
        logger.error('Data not being received. Please check URL')
        logger.info('Level 1 check completed.')
        resp1 = 'NOT OK'
    else:
        logger.info(f'Response Code not expected. Response Code:{resp}')
        logger.info('Level 1 check completed.')
        resp1 = 'NOT OK'
    return (resp1, blocked)




def level1(base_url, method,  meta=None, proxy=None, blocked = None):
    logger = logging.getLogger(__name__)
    # To see if proxy is required
    prox_req = 0
    if (method == 'GET'):
        resp_obj = requests.get(base_url)
    elif (method == 'POST'):
        resp_obj = requests.post(base_url, data=meta, json=None)
    else:
        resp_obj = None
        logger.warning(f'Should this method: {method} really be allowed?\n Response Object is none')
    if(resp_obj == None):
        return 1
    resp_status = resp_obj.status_code
    if(resp_status == 200):
        #print(resp_obj.reason)
        logger.info(f'Response Message:{resp_obj.reason}')
        logger.info("Response Code 200 returned. Stage 1 checking complete. Might still be blocked")
        #print('Nice')
        return resp_status
    else:
        logger.warning(f'Response Code not expected. Response Code:{resp_status}')
        return resp_status


def level2(base_url, conn, doc):
    logger = logging.getLogger(__name__)
    if(conn==None):
        logger.warning(f'Base URL:{base_url}\nSkipping level 2 check as MongoDB conn is None')
        return -1
    resp = conn.find_one({})
    if (resp is None):
        logger.warning(f'{conn} returned empty')
        return -1
    resp = dict(resp)

    print(resp)
    #TODO Change to 0
    format_flag = 0
    logger.debug(sorted(list(resp.keys()))[1:])
    if(sorted(list(resp.keys()))[1:]==sorted(list(doc.keys()))):
        for i in list(doc.keys()):
            if((doc[i] is None ) or (not(doc[i]))):
                logger.warning(f'Base URL:{base_url}\nEmpty Fields in {dict(doc)}')
                format_flag = 1
    else:
        logger.warning(f'Base URL:{base_url}\nKeys do not match. Expected keys:{sorted(list(resp.keys()))[1:]}. Actual keys:{sorted(list(doc.keys()))}')
    if(not format_flag):
        logger.info('Level 2 check completed')
    return format_flag

def count_fn():
    count_fn.count += 1
    return count_fn.count

count_fn.count = 0

def get_tree(ele, tree_list):
    master_tree_list = []
    for i in ele:
        # print(i.tag)
        queue = []
        queue.append([i, 0])
        while queue:
            pop_ele, depth = queue.pop(0)
            # print(pop_ele.tag)
            tree_list.append([pop_ele.tag, pq(pop_ele).attr('class'), pq(pop_ele).attr('id'), count_fn(), depth])
            for j in pq(pop_ele).children():
                queue.append([j, depth + 1])
        master_tree_list.extend(tree_list)
    return master_tree_list

def get_prev_tree_list():
    tree_list = glob.glob('treelist*')
    # print('here in fn')
    # print(tree_list)
    if (len(tree_list) == 0):
        print('never mind')
        return None
    tree_list_sorted = sorted(tree_list, key=os.path.getmtime, reverse=True)
    ref = tree_list_sorted[0]
    f = open(ref)
    ref_obj = json.loads(f.read())
    for i in tree_list_sorted[1:]:
        os.remove(i)
    # print(ref_obj['tree_data'])
    return ref_obj['tree_data']

def level3(base_url, pq_obj):
    logger = logging.getLogger(__name__)
    count_fn.count = 0
    prev_tree_list = get_prev_tree_list()
    pflag = 0
    if(prev_tree_list is None):
        logger.warning('Previous reference file not found. Level 3 check terminated.')
        pflag = 1
    if(prev_tree_list is not None):
        print(type(prev_tree_list))
    tree_list = get_tree(pq_obj.children(), [])
    write_time = datetime.datetime.now()
    json_dict = {'mod_time': write_time.strftime("%d%b%Y%H_%M_%S_%f"), 'tree_data': tree_list}
    f = open(f'treelist{write_time.strftime("%d%b%Y%H_%M_%S_%f")}.json', 'w')
    json.dump(json_dict, f)
    # TODO: DECIDE FN
    if(pflag!=1):
        multipliers = {i: 2 ** -i for i in range(6)}
        new_score = 0
        prev_score = 0
        diff = 0
        for i, j in zip(tree_list, prev_tree_list):
            if (i != j):
                logger.warning(f'Base URL:{base_url}. Mismatch: >{i}\n<{j}')
                diff = 1
        if (diff == 0):
            logger.info(f'Base URL:{base_url}.Level 3 check complete.')
            print('Not Different!')
        return diff
    return -1

if __name__=='__main__':
    requests.get('http://127.0.0.1:5000/reset')
    url = 'http://127.0.0.1:5000/2_retries'
    method = 'POST'
    source_name = 'test'
    MAX_RETRIES = 5
    gen = master_check('https://docs.python.org/3.8/library/multiprocessing.html', source_name, method, MAX_RETRIES)
    next(gen)
    next(gen)
    n = gen.send([None, 'rubbish'])
    #print(n)
    next(gen)
    resp = requests.get('https://docs.python.org/3.8/library/multiprocessing.html')
    gen.send(None)

