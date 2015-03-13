from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse


def front(request):
    return render(request, 'waypoints/index.html', context)



