import sys

import django
from django.conf import settings
from django.test.runner import DiscoverRunner

test_settings = dict(
    DEBUG=True,
    SECRET_KEY='a' * 24,
    ROOT_URLCONF='tests.urls',
    INSTALLED_APPS=[
        'django.contrib.sessions',
    ],
    MIDDLEWARE_CLASSES=[
        'django.contrib.sessions.middleware.SessionMiddleware',
    ],
    SESSION_ENGINE='django.contrib.sessions.backends.signed_cookies',
    TEMPLATES=[{
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': False,
        'OPTIONS': {
            'context_processors': [],
            'loaders': ['tests.utils.DummyTemplateLoader'],
        },
    }],
    GOOGLE_ANALYTICS_ID='UA-12345678-0',
)


def run():
    if not settings.configured:
        settings.configure(**test_settings)
        django.setup()
    failures = DiscoverRunner(verbosity=2, failfast=False, interactive=False).run_tests(['tests'])
    sys.exit(failures)


if __name__ == '__main__':
    run()
