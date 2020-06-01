def ref_check(conn, dictionary):
    resp = conn.find_one({})
    sim = compare(resp,dictionary)
    return sim

def compare(resp, dictionary):
    try:
        if(sorted(list(resp.keys())) != sorted(list(dictionary.keys()))):
            return 0
        for i in list(resp.keys()):
            if(isinstance(resp[i], dict)):
                ret = compare(resp[i], dictionary[i])
                if(ret==0):
                    return 0
            else:
                if(resp[i]!=dictionary[i]):
                    return 0
        return 1
    except KeyError:
        return 0