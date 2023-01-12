Django Form Error Reporting
===========================

A form mixin that reports form errors as events to Google Analytics.

NB: Only Universal Analtics is supported, which is now deprecated!

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

.. image:: https://github.com/ministryofjustice/django-form-error-reporting/actions/workflows/test.yml/badge.svg?branch=main
    :target: https://github.com/ministryofjustice/django-form-error-reporting/actions/workflows/test.yml

.. image:: https://github.com/ministryofjustice/django-form-error-reporting/actions/workflows/lint.yml/badge.svg?branch=main
    :target: https://github.com/ministryofjustice/django-form-error-reporting/actions/workflows/lint.yml

Please report bugs and open pull requests on `GitHub`_.

Use ``python setup.py test`` to run all tests.

Distribute a new version to `PyPi`_ by updating the ``version`` argument in ``setup.py:setup`` and
publishing a release in GitHub (this triggers a GitHub Actions workflow to automatically upload it).
Alternatively, run ``python setup.py sdist bdist_wheel upload`` locally.

Copyright
---------

Copyright (C) 2023 HM Government (Ministry of Justice Digital & Technology).
See LICENSE.txt for further details.

.. _GitHub: https://github.com/ministryofjustice/django-form-error-reporting
.. _PyPi: https://pypi.org/project/django-form-error-reporting/
