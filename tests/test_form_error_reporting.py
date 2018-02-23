import os
import types
import unittest
try:
    from unittest import mock
except ImportError:
    import mock

from django.core.urlresolvers import reverse
from django.http import QueryDict
from django.test import SimpleTestCase
import responses
from six.moves.urllib.parse import urljoin


class FormErrorReportingTestCase(SimpleTestCase):
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
        with mock.patch('form_error_reporting.requests') as mocked_requests:
            self.assertFalse(form.is_valid(), 'Form should be invalid')
            self.assertEqual(mocked_requests.post.call_count, 2)
            for call in mocked_requests.post.call_args_list:
                data = call[1]['data']
                self.assertLessEqual(len(data.encode('utf8')), 16 * 1024,
                                     'Each report cannot be greater than 16kb')
                self.assertLessEqual(len(data.splitlines()), 20,
                                     'There cannot be more than 20 hits per report')

    @mock.patch('tests.utils.get_template_source')
    @mock.patch('tests.urls.get_context')
    def test_form_errors_with_session(self, mocked_context, mocked_template_source):
        from tests.forms import RequestReportedForm

        def get_context(request):
            form = RequestReportedForm(request, data=request.POST)
            return {
                'form': form,
            }

        mocked_context.side_effect = get_context
        mocked_template_source.return_value = '''
        "{{ form.is_valid }}"
        '''

        user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) AppleWebKit/537.36 (KHTML, like Gecko) ' \
                     'Chrome/55.0.2883.95 Safari/537.36'
        with responses.RequestsMock() as rsps:
            rsps.add(rsps.POST, urljoin(RequestReportedForm.ga_endpoint_base, '/batch'))
            response = self.client.post(reverse('dummy'), data={
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
        form.ga_endpoint_base = 'https://ssl.google-analytics.com/debug/'
        form.ga_batch_hits = False
        form.report_errors_to_ga = types.MethodType(report_errors, form)
        form.is_valid()
