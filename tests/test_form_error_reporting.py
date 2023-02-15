import os
import sys
import types
import unittest
from unittest import mock
from urllib.parse import urljoin

import django
from django.http import QueryDict
from django.test import SimpleTestCase
from django.urls import reverse
import responses


class FormErrorReportingTestCase(SimpleTestCase):
    def test_print_django_version(self):
        print(f'Testing on django {django.__version__}', file=sys.stderr)

    def submit_simple_form(self, data):
        from tests.forms import SimpleReportedForm

        form = SimpleReportedForm(data=data)
        form.ga_client_id = form.get_ga_client_id()  # freeze a generated client id
        return form

    def assertResponseErrorsReported(self, rsps, expected_error_dicts):  # noqa
        for expected_error_dict in expected_error_dicts:
            expected_error_dict.update({
                'v': '1',
                'tid': 'UA-12345678-0',
                't': 'event',
            })
        reported_error_dicts = []
        self.assertEqual(len(rsps.calls), 1)
        for error_line in rsps.calls[0].request.body.splitlines():
            if not error_line:
                continue
            error_params = QueryDict(error_line)
            error_params = {k: v for k, v in error_params.items()}
            reported_error_dicts.append(error_params)
        self.assertEqual(len(reported_error_dicts), len(expected_error_dicts))
        error_dict_pairs = zip(reported_error_dicts, expected_error_dicts)
        for reported_error_dict, expected_error_dict in error_dict_pairs:
            self.assertDictEqual(reported_error_dict, expected_error_dict)

    def assertFormErrorsReported(self, form, expected_error_dicts):  # noqa
        with responses.RequestsMock() as rsps:
            rsps.add(rsps.POST, form.get_ga_batch_endpoint())
            self.assertFalse(form.is_valid(), 'Form should be invalid')
            self.assertResponseErrorsReported(rsps, expected_error_dicts)

    def test_no_errors_send_no_reports(self):
        from tests.forms import SimpleReportedForm

        form = SimpleReportedForm(data={
            'required_number': 4,
            'required_text': 'abc',
        })
        with mock.patch.object(SimpleReportedForm, 'report_errors_to_ga', return_value=None) as method:
            self.assertTrue(form.is_valid())
            self.assertFalse(method.called)

    def test_single_field_error_reported(self):
        form = self.submit_simple_form({
            'required_number': 1,
            'required_text': 'abc',
        })
        self.assertFormErrorsReported(form, [
            {
                'cid': form.ga_client_id,
                'ec': 'tests.forms.SimpleReportedForm',
                'ea': 'required_number',
                'el': 'Ensure this value is greater than or equal to 3.',
            },
        ])

    def test_non_field_error_reported(self):
        form = self.submit_simple_form({
            'required_number': 4,
            'required_text': 'abc',
        })
        form.raise_non_field_error = True
        self.assertFormErrorsReported(form, [
            {
                'cid': form.ga_client_id,
                'ec': 'tests.forms.SimpleReportedForm',
                'ea': '__all__',
                'el': 'This form is invalid.',
            },
        ])

    def test_multiple_errors_reported(self):
        form = self.submit_simple_form({
            'required_number': 1,
            'required_text': '',
        })
        form.raise_non_field_error = True
        self.assertFormErrorsReported(form, [
            {
                'cid': form.ga_client_id,
                'ec': 'tests.forms.SimpleReportedForm',
                'ea': '__all__',
                'el': 'This form is invalid.',
            },
            {
                'cid': form.ga_client_id,
                'ec': 'tests.forms.SimpleReportedForm',
                'ea': 'required_number',
                'el': 'Ensure this value is greater than or equal to 3.',
            },
            {
                'cid': form.ga_client_id,
                'ec': 'tests.forms.SimpleReportedForm',
                'ea': 'required_text',
                'el': 'This field is required.',
            },
        ])

    def test_report_batching(self):
        from tests.forms import ManyErrorTestForm

        form = ManyErrorTestForm(data={'required_text': 'abc'})
        with responses.RequestsMock() as rsps:
            rsps.add(rsps.POST, form.get_ga_batch_endpoint())
            self.assertFalse(form.is_valid(), 'Form should be invalid')
            self.assertEqual(len(rsps.calls), 2)
            for call in rsps.calls:
                data = call[0].body
                self.assertLessEqual(len(data.encode('utf8')), 16 * 1024,
                                     'Each report cannot be greater than 16kb')
                self.assertLessEqual(len(data.splitlines()), 20,
                                     'There cannot be more than 20 hits per report')

    def test_form_errors_with_session(self):
        from tests.forms import RequestReportedForm

        user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) AppleWebKit/537.36 (KHTML, like Gecko) ' \
                     'Chrome/55.0.2883.95 Safari/537.36'
        with responses.RequestsMock() as rsps:
            rsps.add(rsps.POST, urljoin(RequestReportedForm.ga_endpoint_base, '/batch'))
            response = self.client.post(reverse('test-form'), data={
                'required_number': 1,
                'required_text': '',
            }, HTTP_USER_AGENT=user_agent)
            client_id = response.client.session.get('ga_client_id')
            self.assertContains(response, '"False"')
            self.assertResponseErrorsReported(rsps, [
                {
                    'cid': client_id,
                    'ec': 'tests.forms.RequestReportedForm',
                    'ea': 'required_number',
                    'el': 'Ensure this value is greater than or equal to 3.',
                    'uip': '127.0.0.1',
                    'ua': user_agent,
                },
                {
                    'cid': client_id,
                    'ec': 'tests.forms.RequestReportedForm',
                    'ea': 'required_text',
                    'el': 'This field is required.',
                    'uip': '127.0.0.1',
                    'ua': user_agent,
                },
            ])

    @unittest.skipIf('GOOGLE_ANALYTICS_ID' not in os.environ,
                     'Provide a valid GOOGLE_ANALYTICS_ID environment variable')
    def test_validate_reporting_format(self):
        from tests.forms import SimpleReportedForm

        report_errors_to_ga = SimpleReportedForm.report_errors_to_ga

        def report_errors(self_, errors):
            super_responses = report_errors_to_ga(self_, errors)
            self.assertEqual(len(super_responses), 1)
            response = super_responses[0].json()['hitParsingResult']
            valid = all(result['valid'] for result in response)
            try:
                error_message = []
                for result in response:
                    result = map(lambda message: '%(messageType)s (%(parameter)s): %(description)s' % message,
                                 result['parserMessage'])
                    error_message.append('\n'.join(result))
                error_message = '----------\n'.join(error_message)
            except KeyError:
                error_message = 'Parser message not readable :('
            self.assertTrue(valid, error_message)
            return super_responses

        form = self.submit_simple_form({
            'required_number': 1,
            'required_text': 'abc',
        })
        form.ga_tracking_id = os.environ['GOOGLE_ANALYTICS_ID']
        form.ga_endpoint_base = 'https://ssl.google-analytics.com/debug/'
        form.ga_batch_hits = False
        form.report_errors_to_ga = types.MethodType(report_errors, form)
        form.is_valid()
