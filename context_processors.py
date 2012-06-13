def is_preview(request):
	from django.conf import settings
	return {'jquery_home': settings.JQUERY_HOME, 'jquery_ui_home': settings.JQUERY_UI_HOME}
	
def count_unseen(request):
	from notification.models import Notice, NoticeManager
	if request.user.is_anonymous():
		count = 0
	else:
		count = Notice.objects.unseen_count_for(request.user)
	return {'unseen_count': count}