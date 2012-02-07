import multiprocessing
import time
import sys
import random

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
    #time.sleep(random.uniform(0,0.1))
    print "in doubler %s " % (n)
    return 2*n

def negator(n):
    #time.sleep(random.uniform(0,0.1))
    print "in negator %s " % (n)
    return -n

def tripler(n):
    #time.sleep(random.uniform(0,0.1))
    print "in tripler %s " % (n)
    return 3*n




class Consumer(multiprocessing.Process):

    def __init__(self, task_queue, result_queue):
        multiprocessing.Process.__init__(self)
        self.task_queue = task_queue
        self.result_queue = result_queue

    def run(self):
        proc_name = self.name
        while True:
            next_task = self.task_queue.get()
            if next_task is None:
                # Poison pill means shutdown
                print '%s: Exiting' % proc_name
                self.task_queue.task_done()
                break
            print '%s: %s' % (proc_name, next_task)
            answer = next_task()
            self.task_queue.task_done()
            self.result_queue.put(answer)
        return


class NetTask(object):
    def __init__(self, n):
        self.n = n
    def __call__(self):
        print "NetTask %s" % (self.n)
        global doubler_pool, negator_pool, tripler_pool
        print doubler_pool, negator_pool, tripler_pool
        
        async_results = [doubler_pool.apply_async(doubler, (self.n,)),
                         negator_pool.apply_async(negator, (self.n,)),
                         tripler_pool.apply_async(tripler, (self.n,))]
        print async_results
        print "NetTask about to return async_results for %s" % (self.n)
        return (self.n, async_results)
        #return (self.n, sum(r.get() for r in async_results))
    def __str__(self):
        return 'Totaler (%d)' % (self.n)

def pooler():
    
    global doubler_pool, negator_pool, tripler_pool
    
    TO_CALC = 10
    results = []
    
    for n in range(TO_CALC):
        async_results = [doubler_pool.apply_async(doubler, (n,)), negator_pool.apply_async(negator, (n,)), tripler_pool.apply_async(tripler, (n,)),]
        results.append(async_results)
        
    for result in results:
        print(sum(r.get() for r in result))
        
def main():
    
    # generate a queue to hold the results
    tasks = multiprocessing.JoinableQueue()
    results_queue = multiprocessing.Queue()
    
    global doubler_pool, negator_pool, tripler_pool
    
    doubler_pool = multiprocessing.Pool(1) #use one core for now
    negator_pool = multiprocessing.Pool(1)
    tripler_pool = multiprocessing.Pool(1)
    
    random.seed()

    # Start consumers
    num_consumers = multiprocessing.cpu_count()
    print 'Creating %d consumers' % num_consumers
    consumers = [ Consumer(tasks, results_queue)
                  for i in xrange(num_consumers) ]
    for w in consumers:
        w.start()    

    # demonstrate that we can do stuff with the pools
    pooler() 
        
    n_tasks = 2
    
    # create a separate process for each totaler operation
    for k in xrange(n_tasks):
        tasks.put(NetTask(k))
        
    # Add a poison pill for each consumer
    for i in xrange(num_consumers):
        tasks.put(None)        
        
    # while there is an expectation of more results, read off results in the results queue
    results_so_far = 0
    net_results = {}
    
    while results_so_far < n_tasks:
        result = results_queue.get()
        net_results[result[0]] = result[1]
        print result
        results_so_far += 1
    
    print "net results", net_results
    
if __name__ == '__main__':
    main()