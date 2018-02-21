import os
import sys

from setuptools import setup

root_path = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(root_path, 'README.rst')) as readme:
    README = readme.read()

tests_require = ['flake8>=3.2', 'responses>=0.5']
if sys.version_info < (3, 3):
    tests_require.append('mock>=1.3')

setup(
    name='django-form-error-reporting',
    version='0.6',
    author='Ministry of Justice Digital Services',
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
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
    ],
    install_requires=['Django>=1.9', 'requests', 'six'],
    tests_require=tests_require,
    test_suite='tests.test_form_error_reporting',
)
