from django.conf import settings


class SpecialDateMixin(object):

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        special_date_name = settings.SPECIAL_DATE_NAME
        context['img'] = settings.SPECIAL_DATE_SETTINGS[
            special_date_name].get('image')
        context['special_date_name'] = special_date_name

        return context
