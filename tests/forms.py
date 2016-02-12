from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError

from form_error_reporting import GAErrorReportingMixin, GARequestErrorReportingMixin


class TestForm(forms.Form):
    required_number = forms.IntegerField(min_value=3)
    required_text = forms.CharField(max_length=10)
    raise_non_field_error = False

    def clean(self):
        cleaned_data = super(TestForm, self).clean()
        if self.raise_non_field_error:
            raise ValidationError('This form is invalid.', code='invalid')
        return cleaned_data


class SimpleReportedForm(GAErrorReportingMixin, TestForm):
    """
    Minimal form - sets the tracking ID class-wide
    """
    ga_tracking_id = settings.GOOGLE_ANALYTICS_ID


class RequestReportedForm(GARequestErrorReportingMixin, TestForm):
    """
    Extended form - saves the HttpRequest object during form instantiation
    """

    def __init__(self, request, **kwargs):
        self.request = request
        super(RequestReportedForm, self).__init__(**kwargs)
