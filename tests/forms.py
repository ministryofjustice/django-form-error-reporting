import uuid

from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError

from form_error_reporting import GoogleAnalyticsErrorReportingMixin


class SimpleReportedForm(GoogleAnalyticsErrorReportingMixin, forms.Form):
    required_number = forms.IntegerField(min_value=3)
    required_text = forms.CharField(max_length=10)
    raise_non_field_error = False

    def get_ga_tracking_id(self):
        return settings.GOOGLE_ANALYTICS_ID

    def clean(self):
        cleaned_data = super(SimpleReportedForm, self).clean()
        if self.raise_non_field_error:
            raise ValidationError('This form is invalid.', code='invalid')
        return cleaned_data


class SessionReportedForm(SimpleReportedForm):
    def __init__(self, request, **kwargs):
        self.request = request
        super(SessionReportedForm, self).__init__(**kwargs)

    def get_ga_client_id(self):
        if 'ga_client_id' not in self.request.session:
            self.request.session['ga_client_id'] = str(uuid.uuid4())
        return self.request.session['ga_client_id']

    def get_ga_query_dict(self):
        user_ip = self.request.META.get('REMOTE_ADDR')
        user_agent = self.request.META.get('HTTP_USER_AGENT')
        query_dict = super(SimpleReportedForm, self).get_ga_query_dict()
        if user_ip:
            query_dict['uip'] = user_ip
        if user_agent:
            query_dict['ua'] = user_agent
        return query_dict
