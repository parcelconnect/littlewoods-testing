from django import template
from django.conf import settings
from django.template.loader import get_template

register = template.Library()


@register.simple_tag
def raveninit():
    """This is necessary because {% load raven %} cannot be included in the
    base template if raven is not installed.
    """
    if settings.RAVEN_CONFIG.get('dsn'):
        tmpl = get_template('load_raven.html')
        return tmpl.render()
    return ''
