from django.conf import settings


class SpecialDateMixin(object):

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        special_date_name = settings.SPECIAL_DATE_NAME
        context['special_date_name'] = special_date_name
        if context['special_date_name']:
            context['background_img'] = settings.SPECIAL_DATE_IMAGE[
                special_date_name]
        else:
            context['background_img'] = 'img/lwi-gift-wrapping-bg.png'

        return context
