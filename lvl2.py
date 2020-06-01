# Field Enforcer
# Purpose: To see if or not, the data that we are receiving matches what we should get
# How?
# 1. Check if certain fields are non-null
# 2. Find something for which the document should be an exact match as before
# What is to be done?
# Get data, get MongoDB document
# Check if exact match, if not then flag
# Input: Base URL, meta-data

import logging
from lvl3 import html_check
def format_check_temp():
    return 0

def format_check(base_url, conn, doc, pq_obj):
    logger = logging.getLogger(__name__)
    if(conn==None):
        logger.warning(f'Base URL:{base_url}\nSkipping level 2 check as MongoDB conn is None')
        return
    resp = dict(conn.find_one({}))
    print(resp)
    #TODO Change to 0
    format_flag = 1
    logger.debug(sorted(list(resp.keys()))[1:])
    if(sorted(list(resp.keys()))[1:]==sorted(list(doc.keys()))):
        for i in list(doc.keys()):
            if(doc[i] is None or not(doc[i])):
                logger.warning(f'Base URL:{base_url}\nEmpty Fields in {dict(doc)}')
                format_flag = 1
        if(format_flag):
            logger.info(f'Initiating level 3 check.')
            html_check(base_url, pq_obj)
    else:
        logger.warning(f'Base URL:{base_url}\nKeys do not match. Expected keys:{sorted(list(resp.keys()))[1:]}. Actual keys:{sorted(list(doc.keys()))}')
