from regluit.core.models import Campaign
from django.http import HttpResponse
import traceback
from django.db import transaction
import time

def test_read(request):
    
    try:
        
        row_id = 1
        
        print "Attempting to read row"
        
        # A read the waits for the exclusive lock for the row
        campaign = Campaign.objects.raw("SELECT * FROM core_campaign WHERE id=%d FOR UPDATE" % row_id)[0]
        
        print "Successfully read row data %d" % campaign.target
        
    except:
        traceback.print_exc()
        
    return HttpResponse("Success")

def test_write(request):
    
    try:
        
        row_id = 1
        campaign = Campaign.objects.get(id=row_id)
        
        print "Attempting to write row via ordinary ORM"
        
        #
        # Modify the data.  This will block if any shared lock (Either FOR UPDATE or LOCK IN SHARED MODE is held
        #
        campaign.target = campaign.target + 10
        campaign.save()
        
        print "Successfully write new row data %d" % campaign.target
        
    except:
        traceback.print_exc()
        
    return HttpResponse("Success")

@transaction.commit_on_success
def test_lock(request):

    try:
        row_id = 1

        print "Attempting to acquire row lock"

        campaign = Campaign.objects.raw("SELECT * FROM core_campaign WHERE id=%d FOR UPDATE" % row_id)[0]

        print "Row lock acquired, modifying data"

        # Modify the data
        campaign.target = campaign.target + 10
        campaign.save()

        #
        # test by sleeping here for 10 seconds.  
        #
        # The FOR UPDATE request will lock the row exclusively.  All write/delete operations require a compatible lock
        # and will block until this transaction is complete.  Some reads will block, but some will not.  If we want to
        # block the read until this transaction is complete, the read should also acquire an exlusive OR a shared lock.
        #
        # As soon as the function completes, the transaction will be committed and the lock released.
        # You can modify the commit_on_success decorator to get different transaction behaviors
        #
        print "Thread sleeping for 10 seconds"
        time.sleep(10)
        print "Thread sleep complete"

    except:
        traceback.print_exc()

    return HttpResponse("Success")

