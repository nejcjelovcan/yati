
from django.conf import settings

DEFAULTS = {
    'LANGUAGES': ('sl', 'sv', 'ko')
}

def get_setting(key, default=None):
    return getattr(settings, 'YATI_%s'%key, DEFAULTS.get(key))
