import os
import sys

from setuptools import setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

tests_require = ['responses>=0.5']
if sys.version_info < (3, 3):
    tests_require.append('mock>=1.3')

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-form-error-reporting',
    version='0.4',
    author='Ministry of Justice Digital Services',
    url='https://github.com/ministryofjustice/django-form-error-reporting',
    py_modules=['form_error_reporting'],
    license='MIT',
    description='A form mixin that reports form errors as events to Google Analytics',
    long_description=README,
    install_requires=['Django>=1.9', 'requests', 'six'],
    classifiers=[
        'Framework :: Django',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
    ],
    test_suite='tests.test_form_error_reporting',
    tests_require=tests_require,
)
