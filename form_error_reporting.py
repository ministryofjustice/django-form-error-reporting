from collections import OrderedDict
from math import ceil
import uuid
import warnings

import requests
from six.moves.urllib.parse import quote, urljoin


class GoogleAnalyticsErrorReportingMixin(object):
    """
    Form mixin that reports form errors to Google Analytics with events
    """
    ga_endpoint_base = 'https://ssl.google-analytics.com/'
    # non-ssl version: http://www.google-analytics.com/
    ga_tracking_id = None
    ga_client_id = None
    ga_event_category = None
    ga_batch_hits = True

    class QueryDict(OrderedDict):
        def urlencode(self):
            output = ('%s=%s' % (k, quote(v)) for k, v in self.items())
            return '&'.join(output)

    def is_valid(self):
        is_valid = super(GoogleAnalyticsErrorReportingMixin, self).is_valid()
        if not is_valid:
            self.report_errors_to_ga(self.errors)
        return is_valid

    def get_ga_single_endpoint(self):
        return urljoin(self.ga_endpoint_base, 'collect')

    def get_ga_batch_endpoint(self):
        return urljoin(self.ga_endpoint_base, 'batch')

    def get_ga_tracking_id(self):
        return self.ga_tracking_id

    def get_ga_client_id(self):
        return self.ga_client_id or str(uuid.uuid4())

    def get_ga_event_category(self):
        return self.ga_event_category or '%s.%s' % (self.__class__.__module__, self.__class__.__name__)

    def get_ga_query_dict(self):
        return self.QueryDict([
            ('v', '1'),
            ('tid', ''),
            ('cid', ''),
            ('t', 'event'),
            ('ec', ''),
            ('ea', ''),
            ('el', ''),
        ])

    def format_ga_hit(self, field_name, error_message):
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
        Report errors to GA
        https://developers.google.com/analytics/devguides/collection/protocol/v1/devguide
        """
        def batches(_hits):
            # Separate hit payloads into batches of 20
            # Block signle hit payloads > 8KB
            # TODO: Perhaps trim single payloads to fit 8KB? e.g. the el & ua parameters
            # Separate out batches into total payloads <= 16KB

            def paginate(_group):
                page_size = 20
                for page in range(int(ceil(len(_group) / page_size))):
                    yield _group[page * page_size:page * page_size + page_size]

            def limit_8kb(payload):
                return len(payload.encode('utf8')) <= 8 * 1024

            def limit_16kb(payload):
                return len(payload.encode('utf8')) <= 16 * 1024

            def separate_groups(_group):
                payload = '\n'.join(_group)
                if limit_16kb(payload):
                    yield payload
                else:
                    group_size = len(_group) // 2
                    yield separate_groups(_group[:group_size])
                    yield separate_groups(_group[group_size:])

            for _hits in paginate(_hits):
                _hits = list(filter(limit_8kb, _hits))
                yield from separate_groups(_hits)

        hits = []
        responses = []
        for field_name in sorted(errors):
            for error_message in errors[field_name]:
                event = self.format_ga_hit(field_name, error_message)
                if event:
                    hits.append(event)

        if self.ga_batch_hits:
            for hit_batch in batches(hits):
                response = requests.post(self.get_ga_batch_endpoint(), data=hit_batch)
                responses.append(response)
        else:
            for hit in hits:
                response = requests.post(self.get_ga_single_endpoint(), data=hit)
                responses.append(response)
        return responses
