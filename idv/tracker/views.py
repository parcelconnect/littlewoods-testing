from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET

from idv.tracker.est_delivery_date import get_est_delivery_date_from_event

from . import domain


def track(request):
    tracking_number = request.GET.get('trackingNumber', '')
    return render(request, 'tracker/track.html', {
        'tracking_number': tracking_number
    })


@require_GET
def get_tracking_events(request):
    if not request.is_ajax():
        data = {'success': False, 'message': 'Only AJAX requests allowed'}
        return JsonResponse(data, status=406)

    label_id = request.GET.get('label_id')
    if not label_id:
        data = {'success': False, 'message': 'A tracking number is required.'}
        return JsonResponse(data, status=400)

    try:
        events = domain.get_tracking_events(label_id)
    except Exception as exc:
        data = {'success': False, 'message': str(exc)}
        return JsonResponse(data, status=400)
    est_delivery_date = get_est_delivery_date_from_event(events[-1])
    return JsonResponse({
        'success': True,
        'label_id': label_id,
        'events': events,
        'est_delivery_day': est_delivery_date.strftime('%d'),
        'est_delivery_day_str': est_delivery_date.strftime('%A'),
        'est_delivery_month': est_delivery_date.strftime('%B %Y')
    }, status=200)
