import multiprocessing
import time
import sys

"""
Task:  for each of the 900 or so Gutenberg ids, calculate seed isbn(s)

a queue to hold the overall task of calculating the seed isbn
a results queue to hold the seed isbn (or error condition/timeout)
separate queues for GoogleBooks, FreebaseBooks, OpenLibrary, thingisbn queries:
    ideally -- they have timeout, retry facility as well as the ability to sense general failure in API
    ideally: caching of results 
ability to persist jobs, suspend, restart

We will take this in steps by first writing toy models and filling them out

"""
def doubler(n):
    result = 2*n
    return 2*n

def negator(n):
    return -n

def tripler(n):
    return 3*n

def totaler(n, results):
    result = doubler(n) + negator(n) + tripler(n)
    results.put((n, result))

def main():
    
    # generate a queue to hold the results
    results = multiprocessing.Queue()
        
    n_tasks = 10
    
    # create a separate process for each totaler operation
    for k in range(n_tasks):
        task = multiprocessing.Process(name='totaler:{0}'.format(k), target=totaler, args=((k,results)))
        task.daemon = False
        task.start()
    
    # while there is an expectation of more results, read off results in the results queue
    results_so_far = 0
    while results_so_far < n_tasks:
        result = results.get()
        print result
        results_so_far += 1
    
    
if __name__ == '__main__':
    main()