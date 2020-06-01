# Block Checker
# Purpose: To see if we're getting blocked or not
# How?
# 1. Check response code
# 2. Check response message
# 3. If response code using proxy and response code not using proxy are different
# 4. If it's in the 400s, 500s for both, and they are the same, then
# What is to be done?
# Allocate proxy, and then retry
# If it works, mark source as requiring proxy
# Input: Base URL, meta-data
import json
import logging
import requests
from lvl2 import format_check, format_check_temp

def block_check(base_url, method,  meta=None, proxy=None, blocked = None):
    if(ret>=max_retries):
        logging.error(f'Base URL:{base_url}: {max_retries} retries completed. ')
        return
    logger = logging.getLogger(__name__)
    #To see if proxy is required
    prox_req = 0
    if(method=='GET'):
        resp_obj = requests.get(base_url)
    elif(method=='POST'):
        resp_obj = requests.post(base_url, data=meta, json=None)
    else:
        resp_obj = None
        logger.warning(f'Should this method: {method} really be allowed?\n Response Object is none')
    if(resp_obj==None):
        return
    resp_status = resp_obj.status_code
    #FIND RESPONSE CODES THAT SHOULD NOT BE ALLOWED
    if(resp_status in [403]):
        print('Not Nice')
        logger.warning(f"Non-200 response code. Response Code:{resp_status}")
        print('Retry?')
        should_retry = input()
        if(should_retry=='y'):
            block_check(base_url, method, meta=meta, proxy=proxy, blocked=blocked)
    elif(resp_status==200):
        print(resp_obj.reason)
        logger.info(f'Response Message:{resp_obj.reason}')
        logger.info("Response Code 200 returned. Stage 1 checking complete. Might still be blocked")
        print('Nice')
        #TODO form doc
        #UNCOMMENT FOR ACTUAL BEHAVIOUR
        #doc = form_doc(resp_obj.text)
        #prox_req = format_check(base_url, conn, doc, pq_obj)
        prox_req = format_check_temp()
        if(prox_req):
            if(proxy is not None):
                f = open('blocked.json', 'a+')
                blockedjson_obj = json.load(f)
                if(base_url in list(blockedjson_obj.keys())):
                    blockedjson_obj[base_url].append(proxy)
                else:
                    blockedjson_obj[base_url] = [proxy]
            # Pass Proxy here
            block_check(base_url,method,retry=ret+1, meta=meta, proxy=None)
    else:
        logger.warning(f'Response Code not expected. Response Code:{resp_status}')

if __name__=='__main__':
    logging.basicConfig(filename='new.txt',filemode='w', level=logging.DEBUG)
    requests.get('http://127.0.0.1:5000/reset')
    block_check('http://127.0.0.1:5000/2_retries','GET')