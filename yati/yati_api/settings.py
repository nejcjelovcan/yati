
from django.conf import settings

DEFAULTS = {
    #'LANGUAGES': ('sl', 'sv', 'ko', 'fr')   @DEPRECATED (use django's prepared settings.LANGUAGES)
}

def get_setting(key, default=None):
    return getattr(settings, 'YATI_%s'%key, DEFAULTS.get(key))
