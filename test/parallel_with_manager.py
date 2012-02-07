import multiprocessing
from functools import partial

def wrap_with_args(f):
    def f1(*args, **kwargs):
        r = f(*args, **kwargs)
        return ((args, tuple(sorted(kwargs.items()))), r) # return hashable components
    return f1

@wrap_with_args
def doubler(n):
    #time.sleep(random.uniform(0,0.1))
    print "in doubler %s " % (n)
    return 2*n

class DoubleTask(object):
    def __init__(self, n):
        self.n = n
    def __call__(self):
        print "DoubleTask %s" % (self.n)
        return (self.n, 2*self.n)
    def __str__(self):
        return 'DoubleTask (%d)' % (self.n)

class ConsumerWithResultDict(multiprocessing.Process):

    def __init__(self, task_queue, result_dict):
        multiprocessing.Process.__init__(self)
        self.task_queue = task_queue
        self.result_dict = result_dict

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
            print "answer: ", answer
            self.task_queue.task_done()
            self.result_dict[answer[0]] = answer[1]
        return
    

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

if __name__ == '__main__':
    
    manager = multiprocessing.Manager()
    
    doubler_queue = multiprocessing.JoinableQueue()
    results = manager.dict()
    
    doubler_processor = ConsumerWithResultDict(doubler_queue, results)
    doubler_processor.start()
    
    n_tasks = 10
    for k in xrange(n_tasks):
        doubler_queue.put(DoubleTask(k))
    doubler_queue.put(None) # mark the end
    
    doubler_queue.join()
    
    print results
    
    