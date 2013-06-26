"""
a command that creates a given number of random tasks to test out celery
"""

import random

from django.core.management.base import BaseCommand

from regluit.core import tasks
from regluit.core.models import CeleryTask

random.seed()

class Command(BaseCommand):
    help = "create random tasks"
    args = "<num_tasks action>"

    def handle(self, num_tasks, action, **options):
        """
        actions:
        
        c: create num_tasks tasks
        s: print state of existing tasks
        d: delete all tasks
        an integer: compute factorial of the integer -- can then follow up with s to find the state 
        """
        import django
        django.db.transaction.enter_transaction_management()
        if action == 'c':
            for i in xrange(int(num_tasks)):
                n = random.randint(1,1000)
                task_id = tasks.fac.delay(n)
                
                ct = CeleryTask()
                ct.task_id = task_id
                ct.function_name = 'fac'
                ct.function_args = n
                ct.description = "Factorial of %d" % (n)
                ct.save()      
        elif action == 's':
            for (i, ct) in enumerate(CeleryTask.objects.all()):
                print i, ct.function_args, ct.state, ct.info
        elif action == 'd':
            CeleryTask.objects.all().delete()
        else:
            try:
                action = int(action)
                print 'action: %d' % (int(action))
                task_id = tasks.fac.delay(int(action),sleep_interval=0.001)
                
                ct = CeleryTask()
                ct.task_id = task_id
                ct.function_name = 'fac'
                ct.function_args = action
                ct.description = "Factorial of %d" % (action)
                ct.save()
            except Exception, e:
                print e
        django.db.transaction.commit()        