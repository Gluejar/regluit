def is_preview(request):
	from django.conf import settings
	return {'is_preview': settings.IS_PREVIEW, 'jquery_home': settings.JQUERY_HOME, 'jquery_ui_home': settings.JQUERY_UI_HOME}