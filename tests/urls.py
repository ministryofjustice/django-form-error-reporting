from django.conf.urls import url
from django.http.response import HttpResponse

from tests.forms import RequestReportedForm


def test_form(request):
    form = RequestReportedForm(request, data=request.POST)
    return HttpResponse('"%s"' % form.is_valid())


urlpatterns = [
    url(r'^$', test_form, name='test-form'),
]
