import multiprocessing as mp
import time
import random
from itertools import izip

def double(x):
    double.q.put('Doing: ' + str(x))
    time.sleep(random.uniform(0,0.1))
    return 2*x

def triple(x):
    triple.q.put('Doing: ' + str(x))
    time.sleep(random.uniform(0,0.1))
    return 3*x

def f(args):
    f.q.put('Doing: ' + str(args))
    return sum(args)

def f_init(q, g):
    g.q = q

def main():
    random.seed()
    jobs = range(1,6)

    q = mp.Queue()
    q_d = mp.Queue()
    q_t = mp.Queue()
    
    p = mp.Pool(None, f_init, [q, f])
    p_d = mp.Pool(None, f_init, [q_d, double])
    p_t = mp.Pool(None, f_init, [q_t, triple])
    
    results_d = p_d.map(double, jobs)
    results_t = p_t.map(triple, jobs)
    
    p_d.close()
    p_t.close()
    
    results0 = izip(results_d, results_t)
    results = p.map(f, results0)
    p.close()
    
    print list(results)


if __name__ == '__main__':
    main()