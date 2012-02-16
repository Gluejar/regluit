import multiprocessing
from multiprocessing import Pipe

class DoubleTask(object):
    def __init__(self, n, conn):
        self.n = n
        self.conn = conn # pipe to send results back
    def __call__(self):
        print "DoubleTask %s" % (self.n)
        self.conn.send((self.n, 2*self.n))
        self.conn.close()
        return (self.n, 2*self.n)
    def __str__(self):
        return 'DoubleTask (%d)' % (self.n)
        
class TripleTask(object):
    def __init__(self, n):
        self.n = n
    def __call__(self):
        print "TripleTask %s" % (self.n)
        return (self.n, 3*self.n)
    def __str__(self):
        return 'TripleTask (%d)' % (self.n)    
    
class BigTask(object):
    def __init__(self, n, doubler_queue):
        self.n = n
        self.doubler_queue = doubler_queue
    def __call__(self):
        print "BigTask %s" % (self.n)
        # put the DoubleTask into the doubler_queue and wait for a result
        parent_conn, child_conn = Pipe()
        
        double_task = self.doubler_queue.put(DoubleTask(self.n, child_conn))
        double_task_answer = parent_conn.recv()
        
        return (self.n, double_task_answer + TripleTask(self.n)())
    def __str__(self):
        return 'BigTask (%d)' % (self.n)       

class SimpleConsumer(multiprocessing.Process):

    def __init__(self, task_queue):
        multiprocessing.Process.__init__(self)
        self.task_queue = task_queue

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
        return answer   

class Consumer(SimpleConsumer):

    def __init__(self, task_queue, result_queue):
        pass

    def run(self):
        pass

    


if __name__ == '__main__':
    
    manager = multiprocessing.Manager()
    
    big_queue = multiprocessing.JoinableQueue()
    doubler_queue = multiprocessing.JoinableQueue()
    triple_queue = multiprocessing.JoinableQueue()
    
    double_results = manager.dict()
    triple_results = manager.dict()
    big_results = multiprocessing.Queue()
    
    doubler_processor = ConsumerWithResultDict(doubler_queue, double_results)
    triple_processor = ConsumerWithResultDict(triple_queue, triple_results)
    big_processor = Consumer(big_queue, big_results)
    
    doubler_processor.start()
    triple_processor.start()
    big_processor.start()
    
    n_tasks = 10
    for k in xrange(n_tasks):
        big_queue.put(BigTask(k, doubler_queue))
        
    doubler_queue.put(None) # mark the end
    triple_queue.put(None)
    big_queue.put(None)
  
    # while there is an expectation of more results, read off results in the results queue
    results_so_far = 0
    net_results = {}
    
    while results_so_far < n_tasks:
        result = big_results.get()
        net_results[result[0]] = result[1]
        print result
        results_so_far += 1
    
    print "net results", net_results    
    
    