from notification import models as notification

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.template.loader import render_to_string
from django.utils.html import strip_tags

class Claim(models.Model):
    STATUSES = ((u'active', u'Claim has been accepted.'),
                (u'pending', u'Claim is pending acceptance.'),
                (u'release', u'Claim has not been accepted.'),
               )
    created = models.DateTimeField(auto_now_add=True)
    rights_holder = models.ForeignKey("RightsHolder", on_delete=models.CASCADE, related_name="claim", null=False)
    work = models.ForeignKey("Work", on_delete=models.CASCADE, related_name="claim", null=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="claim", null=False)
    status = models.CharField(max_length=7, choices=STATUSES, default='active')

    @property
    def can_open_new(self):
        # whether a campaign can be opened for this claim

        #must be an active claim
        if self.status != 'active':
            return False
        #can't already be a campaign
        for campaign in self.campaigns:
            if campaign.status in ['ACTIVE', 'INITIALIZED']:
                return 0 # cannot open a new campaign
            if campaign.status in ['SUCCESSFUL']:
                return 2  # can open a THANKS campaign
        return 1 # can open any type of campaign

    def  __unicode__(self):
        return self.work.title

    @property
    def campaign(self):
        return self.work.last_campaign()

    @property
    def campaigns(self):
        return self.work.campaigns.all()

def notify_claim(sender, created, instance, **kwargs):
    if 'example.org' in instance.user.email or hasattr(instance, 'dont_notify'):
        return
    try:
        (rights, new_rights) = User.objects.get_or_create(
                                    email='rights@ebookfoundation.org',
                                    defaults={'username':'RightsatFEF'}
                                )
    except:
        rights = None
    if instance.user == instance.rights_holder.owner:
        user_list = (instance.user, rights)
    else:
        user_list = (instance.user, instance.rights_holder.owner, rights)
    notification.send(user_list, "rights_holder_claim", {'claim': instance,})

post_save.connect(notify_claim, sender=Claim)

class RightsHolder(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    email = models.CharField(max_length=100, blank=False, default='')
    rights_holder_name = models.CharField(max_length=100, blank=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="rights_holder", null=False)
    approved = models.BooleanField(default=False)
    address =  models.CharField(max_length=400, blank=False, default='')
    mailing =  models.CharField(max_length=400, blank=False, default='')
    telephone = models.CharField(max_length=30, blank=True)
    signer = models.CharField(max_length=100,  blank=False, default='')
    signer_ip = models.CharField(max_length=40,  null=True)
    signer_title = models.CharField(max_length=30,  blank=False, default='')
    signature = models.CharField(max_length=100, blank=False, default='' )

    def __unicode__(self):
        return self.rights_holder_name

def notify_rh(sender, created, instance, **kwargs):
    # don't notify for tests or existing rights holders
    if 'example.org' in instance.email or instance.id < 47:
        return
    try:
        (rights, new_rights) = User.objects.get_or_create(
                                    email='rights@ebookfoundation.org',
                                    defaults={'username':'RightsatFEF'}
                                )
    except:
        rights = None
    user_list = (instance.owner, rights)
    if created:
        notification.send(user_list, "rights_holder_created", {'rights_holder': instance,})
    elif instance.approved:
        agreement = strip_tags(
            render_to_string(
                'accepted_agreement.html',
                {'rights_holder': instance,}
            )
        )
        signature = ''
        notification.send(
            user_list,
            "rights_holder_accepted",
            {'rights_holder': instance, 'agreement':agreement, 'signature':signature, }
        )
        for claim in instance.claim.filter(status='pending'):
            claim.status = 'active'
            claim.save()
    from regluit.core.tasks import emit_notifications
    emit_notifications.delay()

post_save.connect(notify_rh, sender=RightsHolder)
