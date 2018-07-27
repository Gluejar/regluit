def is_preview(request):
    from django.conf import settings
    return {
        'jquery_home': settings.JQUERY_HOME,
        'jquery_ui_home': settings.JQUERY_UI_HOME,
        'jquery_ui_theme': settings.JQUERY_UI_THEME,
        'is_preview': settings.IS_PREVIEW,
        'show_google_analytics': settings.SHOW_GOOGLE_ANALYTICS
    }

def count_unseen(request):
    try:
        if request.user.is_anonymous:
            count = 0
        else:
            from notification.models import Notice
            count = Notice.objects.unseen_count_for(request.user)
    except AttributeError:
        count = 0
    return {'unseen_count': count}