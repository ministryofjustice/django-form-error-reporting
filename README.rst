Django Form Error Reporting
===========================

A form mixin that reports form errors as events to Google Analytics.

Installation
------------

.. code-block:: bash

    pip install git+https://github.com/ministryofjustice/django-form-error-reporting.git

Usage
-----

See examples in tests/forms.py

.. code-block:: python

    class ReportedForm(GoogleAnalyticsErrorReportingMixin, Form):
        ga_tracking_id = 'UA-12345678-0'

        ...

Testing
-------

.. code-block:: bash

    python setup.py test

Copyright
---------

Copyright |copy| 2016 HM Government (Ministry of Justice Digital Services). See
LICENSE for further details.

.. |copy| unicode:: 0xA9 .. copyright symbol
