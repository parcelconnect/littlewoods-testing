import os

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template


def create_mail(subject, template_prefix, emails, context={}, app_name=None):
    if app_name:
        path_parts = ['mail', app_name, template_prefix]
    else:
        path_parts = ['mail', template_prefix]
    template_path_without_extension = os.path.join(*path_parts)

    plaintext = get_template('{}.txt'.format(template_path_without_extension))
    text_content = plaintext.render(context)

    html = get_template('{}.html'.format(template_path_without_extension))
    html_content = html.render(context)

    from_email = settings.DEFAULT_FROM_EMAIL
    msg = EmailMultiAlternatives(subject, text_content, from_email, emails)
    msg.attach_alternative(html_content, "text/html")

    return msg
