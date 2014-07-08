import csv
import json
import datetime
from decimal import Decimal as D
#import Tkinter, tkFileDialog
from StringIO import StringIO
from regluit.core.models import Campaign

#root = Tkinter.Tk()
#root.withdraw()
last_month = datetime.datetime.today().month -1
last_month = 12 if last_month==0 else last_month
#stripe_reader= csv.DictReader(open(tkFileDialog.askopenfilename(),'rb'), dialect="excel")
stripe_reader= csv.DictReader(open('/Users/eric/Downloads/stripe.csv','rb'), dialect="excel")
royalties_due={}
for purchase in stripe_reader:
    created = purchase['Created']
    paid = purchase['Status'] == 'Paid'
    created_date = datetime.datetime.strptime(created, '%Y-%m-%d %H:%M')
    if (created_date.month == last_month) and paid:
        description = purchase['Description']
        if description and description[0]=='{':
            description = json.load(StringIO(description))
            campaign_id = description['tc.id']
            try:
                campaign = Campaign.objects.get(id = campaign_id)
                #print campaign.name
            except Campaign.DoesNotExist:
                print 'missing campaign:'+ campaign_id
                continue
            if royalties_due.has_key(campaign.id):
                royalty_due = royalties_due[campaign.id].royalty_due
            else:
                royalty_due = D(0)
            if campaign.type==2:
                #b2U
                royalty_due = royalty_due + (D(purchase['Amount']))*D(0.75) -D(0.25)
            elif campaign.type==3:
                #t4u
                royalty_due = royalty_due + (D(purchase['Amount']))*D(0.92) -D(0.25)
            else:
                continue
            campaign.royalty_due=royalty_due
            royalties_due[campaign.id]=campaign
for campaign in royalties_due.values():
    print campaign.rightsholder + ' '+campaign.name+' '+str(campaign.royalty_due)