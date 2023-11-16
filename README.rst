Django Form Error Reporting
===========================

**DEPRECATED**: We have decided to not update this package to support GA4 and this is
no longer maintained.

A form mixin that reports form errors as events to Google Analytics.

NB: Only Universal Analytics is supported, which is now deprecated!

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

To work on changes to this library, it’s recommended to install it in editable mode into a virtual environment,
i.e. ``pip install --editable .``

Use ``python -m tests`` to run all tests locally.
Alternatively, you can use ``tox`` if you have multiple python versions.

[Only for GitHub team members] Distribute a new version to `PyPI`_ by:

- updating the ``VERSION`` tuple in ``form_error_reporting.py``
- adding a note to the `History`_
- publishing a release on GitHub which triggers an upload to PyPI;
  alternatively, run ``python -m build; twine upload dist/*`` locally

History
-------

0.12
    Migrated test, build and release processes away from deprecated setuptools commands.
    No significant library changes.

0.11
    Warn that only Universal Analytics is supported at present.
    Drop support for python 3.6 and 3.7.
    Add support for python 3.11.
    Add experimental support for Django versions 4.0 & 4.1.
    Improve testing and linting.

0.10
    Add support for python 3.9 and 3.10.
    Improve testing and linting.

0.9
    Drop support for python 3.5.
    Improve linting.

0.8
    Drop python 2 support (now compatible with 3.5 - 3.8).
    Support Django 2.2 - 3.2 (both LTS).

0.7
    Improve testing.

0.6
    Fix versioning problem (module cannot be loaded until dependencies are installed).

0.5
    Report user language preference.
    Better IP address tracking for proxied requests.
    Add error logging for failed requests.
    Fix large payload bug.

0.4
    Ignore all errors when reporting to Google Analytics.

0.3
    Add python 2 compatibility.

0.2
    Add convenience form mixin to get Google Analytics ids from request and settings.

0.1
    Original release.

Copyright
---------

Copyright (C) 2023 HM Government (Ministry of Justice Digital & Technology).
See LICENSE.txt for further details.

.. _GitHub: https://github.com/ministryofjustice/django-form-error-reporting
.. _PyPI: https://pypi.org/project/django-form-error-reporting/
