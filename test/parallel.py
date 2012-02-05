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
    return 2*n

def negator(n):
    return -n

def tripler(n):
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
        #time.sleep(0.1) # pretend to take some time to do the work
        result = doubler(self.n) + negator(self.n) + tripler(self.n)
        return (self.n, result)
    def __str__(self):
        return 'Totaler (%d)' % (self.n)
        
def main():
    
    # generate a queue to hold the results
    tasks = multiprocessing.JoinableQueue()
    results = multiprocessing.Queue()
    
    # Start consumers
    num_consumers = multiprocessing.cpu_count()
    print 'Creating %d consumers' % num_consumers
    consumers = [ Consumer(tasks, results)
                  for i in xrange(num_consumers) ]
    for w in consumers:
        w.start()    
        
    n_tasks = 10
    
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
        result = results.get()
        net_results[result[0]] = result[1]
        print result
        results_so_far += 1
    
    print "net results", net_results
    
if __name__ == '__main__':
    main()