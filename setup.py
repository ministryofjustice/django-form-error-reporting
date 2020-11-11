#!/usr/bin/env python
import os
import sys
import warnings

from setuptools import setup

if sys.version_info[0:2] < (3, 6):
    warnings.warn('This package is tested with Python version 3.6+')

root_path = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(root_path, 'README.rst')) as readme:
    README = readme.read()

install_requires = ['Django>=2.2,<4', 'requests']
tests_require = [
    'flake8', 'flake8-bugbear', 'flake8-quotes', 'flake8-blind-except', 'flake8-debugger', 'pep8-naming',
    'responses',
]

setup(
    name='django-form-error-reporting',
    version='0.8',
    author='Ministry of Justice Digital & Technology',
    author_email='dev@digital.justice.gov.uk',
    url='https://github.com/ministryofjustice/django-form-error-reporting',
    py_modules=['form_error_reporting'],
    license='MIT',
    description='A form mixin that reports form errors as events to Google Analytics',
    long_description=README,
    keywords='django form errors google-analytics',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    install_requires=install_requires,
    tests_require=tests_require,
    test_suite='tests.run',
)
