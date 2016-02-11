from django.conf.urls import url
from django.shortcuts import render


def get_context(request):
    # mock this function in tests
    return {}


def dummy_view(request):
    return render(request, 'dummy.html', context=get_context(request))


urlpatterns = [
    url(r'^dummy$', dummy_view, name='dummy'),
]
