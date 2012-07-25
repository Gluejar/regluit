from django.core.management.base import BaseCommand

import django
import sys
from regluit.core.models import Campaign
from regluit.payment.models import Transaction
from django.db.models import Q, F, Count, Sum, Max
from django.contrib.auth.models import User
from regluit.payment.manager import PaymentManager
from decimal import Decimal as D

from collections import defaultdict

from regluit.experimental.gutenberg import unicode_csv

# compare to https://unglue.it/work/81724/acks/

# possible options -- these are options that are relevant in how we would determine what we ask people and what they get
# no implementation of these options however

# should transactions be No premium selected be given nothing by default or maximum benefits for their amount by default?

KEEP_NULL_PREMIUM = False

# should people who explicitly picked a lesser premium be given that premium or the maximum one by default?

KEEP_LESSER_PREMIUM = False

# anonymous by default?

ANONYMOUS_BY_DEFAULT = False

# list of OLA premium ids and pledge amount required for that premium
OLA_PREMIUMS_AND_AMOUNTS = ((1L, D('1')), (97L, D('7')), (2L, D('25')), (98L, D('40')), (3L, D('50')), (99L, D('75')), (4L, D('100')), (15L, D('200')), (18L, D('500')), (65L, D('1000')))
# just the premium ids
OLA_PREMIUM_IDS = tuple([x[0] for x in OLA_PREMIUMS_AND_AMOUNTS])
# just the premium amount levels
LEVELS = tuple([x[1] for x in OLA_PREMIUMS_AND_AMOUNTS])
# mapping of premium amount to id -- assumes only one premium can have the same amount
OLA_PREMIUM_FOR_AMOUNT = dict([(n,m) for (m,n) in OLA_PREMIUMS_AND_AMOUNTS])

# each premium is composed of "material benefits" and acknowledgement levels

# mapping of the material benefits for each premium
MATERIAL_FOR_PREMIUM = dict([(1L, (1,)),
                        (97L, (1, 2)),
                        (2L,  (1, 2)),
                        (98L , (1,3)),
                        (3L, (1,3)),
                        (99L, (1,4)), 
                        (4L, (1,4)),
                        (15L, (1,4,5,6)), 
                        (18L, (1,4,5,7,8)),
                        (65L, (1,4,7,9,10,11))
])

# acknowledgement level for each premium
ACK_FOR_PREMIUM = dict([
    (1L, ()), (97L, ()), (2L, ('A',)), (98L, ('A',)), (3L, ('B',)), (99L, ('B',)), (4L,('C',)), (15L,('C','D')), (18L, ('C','D')), (65L, ('C', 'D'))
])

# the material premiums cluster in the following way -- it makes sense to be able to have 0 or 1 of the specific material
# premiums in a cluster since within a cluster, they are essentially versions of different quality
# 1
# 2, 3, 4
# 5, 9
# 6, 8 , 11
# 7
# 10

MATERIAL_CLUSTERS = ((1,), (2,3,4), (5,9), (6, 8, 11), (7,), (10,))

MATERIAL_PREMIUMS = dict([(1, "The unglued ebook delivered to your inbox."),
    (2, "You will have the choice of one free digital edition selected from our list of published titles. (Offer valid until 30 September 2012)"),
    (3, "You may select one free paperback edition or three free digital editions from our list of published titles. (Offer valid until 30 September 2012.)"),
    (4, "You may select one free hardback edition, or two free paperback editions, or six free digital editions from our list of published titles. (Offer valid until 30 September 2012.)"),
    (5, "A free printed paperback edition with personalised message from the author acknowledging your support."),
    (6, "10% discount on any orders made for printed or digital editions of this, or any other OBP title, from the Open Book Publishers website for 12 months. "),
    (7, "Opportunity to hold either a personal conversation or a webinar with Dr. Mark Turin, Director of the World Oral Literature Project to discuss the project and broader issues surrounding protecting oral literature globally."),
    (8, "20% discount on any orders made for printed or digital editions of this, or any other OBP title, from the Open Book Publishers website for 12 months."),
    (9, "Creation of a special personal benefactor's hardback edition of the title with personalised cover and front page and author's inscription. You will also be able to order additional copies of your personalised edition directly from us at $35 per copy plus shipping."),
    (10, "Free registration and two nights' accommodation to attend the World Oral Literature Project Workshop in Cambridge, England (29-30 June) or a similar future event."),
    (11, "30% discount on any orders made for printed or digital editions of this, or any other OBP title, from the Open Book Publishers website for 12 months.")])

ACKNOWLEDGEMENT_LEVELS = dict([
    ('A', {'label':"""Your username under "supporters" in the acknowledgements section.""", 'parts':('username',)}),
    ('B', {'label':'Your username and profile URL of your choice under "benefactors"', 'parts':('username', 'home_url')}),
    ('C', {'label':'Your username, profile URL, and profile tagline under "bibliophiles"', 'parts':('username', 'home_url', 'tagline')}),
    ('D', {'label':"Your name recorded on a special benefactors' page in all printed and digital editions of the work.", 'parts':('username','email')})
    ])

def supporters_for_campaign(c):
    for k in c.transaction_set.filter(status='Complete').values_list('user',flat=True).order_by('-amount'):
        yield User.objects.get(id=k)
    
def highest_eligible_premium(amount, levels):
    return max(filter(lambda x: x <= amount, levels))

def premiums_and_acks(c):
    """ calculate charts of premiums and acknowledgements owed"""

    for (i, u) in enumerate(supporters_for_campaign(c)):
        try:
            t = c.transaction_set.get(user=u, status='Complete')
            max_premium_amount = highest_eligible_premium(t.amount, LEVELS)
            max_premium_id = OLA_PREMIUM_FOR_AMOUNT[max_premium_amount]
            row = {
                "id":t.id, 
                "username": t.user.username,
                "email": t.user.email,
                "home_url": t.user.profile.home_url, 
                "tagline": t.user.profile.tagline, 
                "amount": t.amount, 
                "premium_id": t.premium.id if t.premium is not None else None, 
                "premium_amount": t.premium.amount if t.premium is not None else None,
                "max_premium_id": max_premium_id,
                "max_premium_amount": max_premium_amount, 
                "material_premium": ",".join([str(x) for x in MATERIAL_FOR_PREMIUM[max_premium_id]]),
                "ack": ",".join(ACK_FOR_PREMIUM[max_premium_id])
            }
            yield row
            
        except Exception, e:
            print "problem: ", i, u, e

        
def out_csv(c, out_fname = "/Users/raymondyee/Downloads/ola_fulfill.csv"):
    
    out_headers = ["id",
            "username", 
            "email",
            "home_url",
            "tagline",
            "amount",
            "premium_id",
            "premium_amount",
            "max_premium_id",
            "max_premium_amount",
            "material_premium",
            "ack"
            ]    
    
    f = open(out_fname, "wb")
    f = unicode_csv.output_to_csv(f, out_headers, premiums_and_acks(c))
        
def benefits_acks_by_category(c):
    """loop through all the transactions and classify into buckets for material premiums + acks"""
    material_benefits_recipients = defaultdict(list)
    ack_recipients = defaultdict(list)
    
    for p in premiums_and_acks(c):
        material_premium = [int(s) for s in p["material_premium"].split(",")]
        ack = p["ack"].split(",")
        for mp in material_premium:
            material_benefits_recipients[mp].append(p)
        for a in ack:
            ack_recipients[a].append(p)
            
    # now print out the materials categories working through the material clusters
    
    for cluster in MATERIAL_CLUSTERS:
        for mp in cluster:
            print "[{0}]".format(mp), MATERIAL_PREMIUMS[mp], "({0})".format( len(material_benefits_recipients[mp]))
            for p in material_benefits_recipients[mp]:
                print p["email"]
            print
            print
        
    for a in sorted(ACKNOWLEDGEMENT_LEVELS.keys()):
        """ for various levels of acknowledgements, write out the different pieces"""
        print "[{0}]".format(a), ACKNOWLEDGEMENT_LEVELS[a]['label'], "({0})".format(len(ack_recipients[a]))
        for p in ack_recipients[a]:
            print "\t".join([p[e] for e in ACKNOWLEDGEMENT_LEVELS[a]["parts"]])
        print
        print
        
    # compare with Eric's calculation of various ack levels
    ungluers = c.ungluers()
    print
    print
    print "supporters match?", set([u.username for u in ungluers["supporters"]]) == set([p['username'] for p in ack_recipients['A']])
    print "patrons match?", set([u.username for u in ungluers["patrons"]]) == set([p['username'] for p in ack_recipients['B']])
    print "bibliophiles match?", set([u.username for u in ungluers["bibliophiles"]]) == set([p['username'] for p in ack_recipients['C']])
    

def validate_c3(c3):
        
    # enumerate the various premiums and how many people have chosen them
    # confirm that there are the same premiums as assumed in operation
    assert (c3.name == 'Oral Literature in Africa')
    assert set([p.id for p in c3.effective_premiums()]) == set(OLA_PREMIUM_IDS)
    assert set([(p.id, p.amount) for p in c3.effective_premiums()]) == set(OLA_PREMIUMS_AND_AMOUNTS)
    # confirm that no one has a premium valued greater than transaction
    assert c3.transaction_set.filter(Q(status='Complete') & Q(premium__isnull=False)).filter(amount__lt = F('premium__amount')).count() == 0
    
def overall_stats(c3):
    print "total number of pledges completed", c3.transaction_set.filter(status='Complete').count()
    
    print "number of pledgers that did not pick any premium", c3.transaction_set.filter(status='Complete').filter(premium__isnull=True).count()
    
    for p in c3.transaction_set.filter(Q(status='Complete') & Q(premium__isnull=False)).order_by('premium__amount').values_list('premium', 'premium__amount').annotate(count_premium=Count('premium')):
        print p[0], p[1], p[2]            
   
    # who deliberately picked premiums at a value level equal to the pledge amount
    print "number of transactions with amount equal to premium amount", c3.transaction_set.filter(Q(status='Complete') & Q(premium__isnull=False)).filter(amount = F('premium__amount')).count()
        

class Command(BaseCommand):
    help = "Displays data about how related to collecting information about premiums for Oral Literature in Africa"
    # args = "<filename> <username>"
    
    def handle(self, **options):
        # this is meant specifically for OLA -- check whether such a compaign is in the db
        c3 = Campaign.objects.get(id=3)
        validate_c3(c3)
        
        overall_stats(c3)
        
        out_csv(c3)
        
        benefits_acks_by_category(c3)