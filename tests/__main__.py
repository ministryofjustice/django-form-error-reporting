import pathlib
import sys

if __name__ == '__main__':
    import django
    from django.conf import settings
    from django.test.runner import DiscoverRunner

    tests_path = pathlib.Path(__file__).parent
    root_path = tests_path.parent

    test_settings = dict(
        DEBUG=True,
        SECRET_KEY='a' * 24,
        ROOT_URLCONF='tests.urls',
        INSTALLED_APPS=(
            'django.contrib.sessions',
        ),
        MIDDLEWARE=[
            'django.contrib.sessions.middleware.SessionMiddleware',
        ],
        SESSION_ENGINE='django.contrib.sessions.backends.signed_cookies',
        TEMPLATES=[{
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [],
        }],
        GOOGLE_ANALYTICS_ID='UA-12345678-0',
    )

    if not settings.configured:
        settings.configure(**test_settings)
        django.setup()

    test_runner = DiscoverRunner(verbosity=2, failfast=False, interactive=False)
    failures = test_runner.run_tests(['tests'])
    sys.exit(failures)
