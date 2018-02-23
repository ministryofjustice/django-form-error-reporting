Django Form Error Reporting
===========================

A form mixin that reports form errors as events to Google Analytics.

Usage
-----

Install using ``pip install django-form-error-reporting``.

See examples in tests/forms.py

.. code-block:: python

    class ReportedForm(GAErrorReportingMixin, Form):
        ga_tracking_id = 'UA-12345678-0'

        ...

Development
-----------

.. image:: https://travis-ci.org/ministryofjustice/django-form-error-reporting.svg?branch=master
    :target: https://travis-ci.org/ministryofjustice/django-form-error-reporting

Please report bugs and open pull requests on `GitHub`_.

Use ``python setup.py test`` to run all tests.

Distribute a new version by updating the ``version`` argument in ``setup.py:setup`` and run ``python setup.py sdist bdist_wheel upload``.

Copyright
---------

Copyright (C) 2018 HM Government (Ministry of Justice Digital Services).
See LICENSE.txt for further details.

.. _GitHub: https://github.com/ministryofjustice/django-form-error-reporting
