from datetime import datetime

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET

from . import domain


def track(request):
    return render(request, 'tracker/track.html')


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

    return JsonResponse({
        'success': True,
        'label_id': label_id,
        'events': events,
        'today': datetime.now().strftime('%B %d, %Y')
    }, status=200)
