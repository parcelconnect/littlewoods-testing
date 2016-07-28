from django.shortcuts import render


def track(request):
    return render(request, 'tracker/track.html')
