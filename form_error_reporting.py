from collections import OrderedDict
import logging
from urllib.parse import quote, urljoin

from math import ceil
import re
import uuid
import warnings

from django.conf import settings
import requests

__all__ = ('GAErrorReportingMixin', 'GARequestErrorReportingMixin')

logger = logging.getLogger(__name__)


class OrderedQueryDict(OrderedDict):
    """
    A simplified version of django.http.request.QueryDict
    that preserves key order
    """

    def urlencode(self):
        """
        Convert dictionary into a query string; keys are
        assumed to always be str
        """
        output = ('%s=%s' % (k, quote(v)) for k, v in self.items())
        return '&'.join(output)


class GAErrorReportingMixin:
    """
    Form mixin that reports form errors to Google Analytics with events
    """
    ga_endpoint_base = 'https://ssl.google-analytics.com/'
    # NB: non-ssl version is http://www.google-analytics.com/
    ga_tracking_id = None
    ga_client_id = None
    ga_event_category = None
    ga_batch_hits = True

    def is_valid(self):
        """
        Error reporting is triggered when a form is checked for validity
        """
        is_valid = super(GAErrorReportingMixin, self).is_valid()
        if self.is_bound and not is_valid:
            try:
                self.report_errors_to_ga(self.errors)
            except:  # noqa: E722
                logger.exception('Failed to report form errors to Google Analytics')
        return is_valid

    def get_ga_single_endpoint(self):
        """
        URL for collecting a single hit
        """
        return urljoin(self.ga_endpoint_base, 'collect')

    def get_ga_batch_endpoint(self):
        """
        URL for collecting multiple hits
        """
        return urljoin(self.ga_endpoint_base, 'batch')

    def get_ga_tracking_id(self):
        """
        Google Analytics ID
        """
        return self.ga_tracking_id

    def get_ga_client_id(self):
        """
        Client ID by which multiple requests are tracked
        """
        return self.ga_client_id or str(uuid.uuid4())

    def get_ga_event_category(self):
        """
        Event category, defaults to form class name
        """
        return self.ga_event_category or '%s.%s' % (self.__class__.__module__, self.__class__.__name__)

    def get_ga_query_dict(self):
        """
        Default hit parameters
        """
        return OrderedQueryDict([
            ('v', '1'),
            ('tid', ''),
            ('cid', ''),
            ('t', 'event'),
            ('ec', ''),
            ('ea', ''),
            ('el', ''),
        ])

    def format_ga_hit(self, field_name, error_message):
        """
        Format a single hit
        """
        tracking_id = self.get_ga_tracking_id()
        if not tracking_id:
            warnings.warn('Google Analytics tracking ID is not set')
            return None
        query_dict = self.get_ga_query_dict()
        query_dict['tid'] = tracking_id
        query_dict['cid'] = self.get_ga_client_id()
        query_dict['ec'] = self.get_ga_event_category()
        query_dict['ea'] = field_name
        query_dict['el'] = error_message
        return query_dict.urlencode()

    def report_errors_to_ga(self, errors):
        """
        Report errors to Google Analytics
        https://developers.google.com/analytics/devguides/collection/protocol/v1/devguide
        """
        hits = []
        responses = []
        for field_name in sorted(errors):
            for error_message in errors[field_name]:
                event = self.format_ga_hit(field_name, error_message)
                if event:
                    hits.append(event)

        if self.ga_batch_hits:
            for hit_batch in _batch_hits(hits):
                response = requests.post(self.get_ga_batch_endpoint(), data=hit_batch)
                responses.append(response)
        else:
            for hit in hits:
                response = requests.post(self.get_ga_single_endpoint(), data=hit)
                responses.append(response)
        return responses


class GARequestErrorReportingMixin(GAErrorReportingMixin):
    """
    Form mixin that reports form errors to Google Analytics with events,
    taking additional information from the HttpRequest object that should be
    set in the __init__ method of subclasses. This mixin also assumes the
    Google Analytics tracking ID is provided in the Django settings.
    """
    ga_tracking_id_settings_key = 'GOOGLE_ANALYTICS_ID'
    ga_cookie_re = re.compile(r'^GA\d+\.\d+\.(?P<cid>.*)$', re.I)

    def get_ga_tracking_id(self):
        """
        Retrieve tracking ID from settings
        """
        if hasattr(settings, self.ga_tracking_id_settings_key):
            return getattr(settings, self.ga_tracking_id_settings_key)
        return super(GARequestErrorReportingMixin, self).get_ga_tracking_id()

    def get_ga_request(self):
        """
        Retrieve current HttpRequest from this form instance
        """
        if hasattr(self, 'request'):
            return self.request

    def get_ga_client_id(self):
        """
        Retrieve the client ID from the Google Analytics cookie, if available,
        and save in the current session
        """
        request = self.get_ga_request()
        if not request or not hasattr(request, 'session'):
            return super(GARequestErrorReportingMixin, self).get_ga_client_id()
        if 'ga_client_id' not in request.session:
            client_id = self.ga_cookie_re.match(request.COOKIES.get('_ga', ''))
            client_id = client_id and client_id.group('cid') or str(uuid.uuid4())
            request.session['ga_client_id'] = client_id
        return request.session['ga_client_id']

    def get_ga_query_dict(self):
        """
        Adds user agent and IP to the default hit parameters
        """
        query_dict = super(GARequestErrorReportingMixin, self).get_ga_query_dict()
        request = self.get_ga_request()
        if not request:
            return query_dict
        user_ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', ''))
        user_ip = user_ip.split(',')[0].strip()
        user_agent = request.META.get('HTTP_USER_AGENT')
        user_language = request.META.get('HTTP_ACCEPT_LANGUAGE')
        if user_ip:
            query_dict['uip'] = user_ip
        if user_agent:
            query_dict['ua'] = user_agent
        if user_language:
            query_dict['ul'] = user_language
        return query_dict


def _batch_hits(hits):
    # Separate hit payloads into batches of 20
    # Block single hit payloads > 8KB
    # TODO: Perhaps trim single payloads to fit 8KB? e.g. the el & ua parameters
    # Separate out batches into total payloads <= 16KB

    def paginate(group):
        page_size = 20
        for page in range(int(ceil(len(group) / page_size))):
            yield group[page * page_size:page * page_size + page_size]

    def limit_8kb(payload):
        return len(payload.encode('utf8')) <= 8 * 1024

    def limit_16kb(payload):
        return len(payload.encode('utf8')) <= 16 * 1024

    def separate_groups(group):
        payload = '\n'.join(group)
        if limit_16kb(payload):
            yield payload
        else:
            group_size = len(group) // 2
            for payload in separate_groups(group[:group_size]):
                yield payload
            for payload in separate_groups(group[group_size:]):
                yield payload

    for hits_page in paginate(hits):
        hits_page = list(filter(limit_8kb, hits_page))
        for hit_group in separate_groups(hits_page):
            yield hit_group
