def is_preview(request):
	from django.conf import settings
	return {'is_preview': settings.IS_PREVIEW}