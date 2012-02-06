import time
import timeit
import random
import multiprocessing

import requests

"""
Fire up various threads to unglue.it / please.unglueit.com to see how much load can be handled.

"""

def get_with_time(url, label=None):
    print "get_with_time: %s" % (label)
    time0 = time.time()
    page = requests.get(url).content
    time1 = time.time()
    return (page, time1-time0, label)

if __name__ == '__main__':
    
    n_calls = 100
    n_workers = 25
    pool =  multiprocessing.Pool(n_workers)
    
    url = "http://unglue.it/lists/popular"
    
    results = [pool.apply_async(get_with_time, (url,k)) for k in xrange(n_calls)]
    print [result.get()[1] for result in results]
    
    

    
