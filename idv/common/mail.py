import os

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template


def create_mail(subject, template_prefix, emails, context={}, app_name=None):
    """
    Create an email ready to be sent (or attach files etc. before sent).
    If `app_name` is set, the template will be loaded from
    templates/mail/[app_name]/, else templates/mail/ will be used.

    Args:
        subject (str): The subject of the email to be sent
        template_prefix (str): The template filename without its extension
        emails (list of str): The email recipients
        context (dict): Context to populate the email template with
        app_name (str):
    Returns:
        django.core.mail.EmailMultiAlternatives obj
    """
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
