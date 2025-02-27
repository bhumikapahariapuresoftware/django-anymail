#!/usr/bin/env python

# python setup.py test
#   or
# runtests.py [tests.test_x tests.test_y.SomeTestCase ...]

import sys

import django
import os
import warnings
from django.conf import settings
from django.test.utils import get_runner


def setup_and_run_tests(test_labels=None):
    """Discover and run project tests. Returns number of failures."""
    test_labels = test_labels or ['tests']

    tags = envlist('ANYMAIL_ONLY_TEST')
    exclude_tags = envlist('ANYMAIL_SKIP_TESTS')

    # In automated testing, don't run live tests unless specifically requested
    if envbool('CONTINUOUS_INTEGRATION') and not envbool('ANYMAIL_RUN_LIVE_TESTS'):
        exclude_tags.append('live')

    if tags:
        print("Only running tests tagged: %r" % tags)
    if exclude_tags:
        print("Excluding tests tagged: %r" % exclude_tags)

    warnings.simplefilter('default')  # show DeprecationWarning and other default-ignored warnings

    os.environ['DJANGO_SETTINGS_MODULE'] = \
        'tests.test_settings.settings_%d_%d' % django.VERSION[:2]
    django.setup()

    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=1, tags=tags, exclude_tags=exclude_tags)
    return test_runner.run_tests(test_labels)


def runtests(test_labels=None):
    """Run project tests and exit"""
    # Used as setup test_suite: must either exit or return a TestSuite
    failures = setup_and_run_tests(test_labels)
    sys.exit(bool(failures))


def envbool(var, default=False):
    """Returns value of environment variable var as a bool, or default if not set/empty.

    Converts `'true'` and similar string representations to `True`,
    and `'false'` and similar string representations to `False`.
    """
    # Adapted from the old :func:`~distutils.util.strtobool`
    val = os.getenv(var, '').strip().lower()
    if val == '':
        return default
    elif val in ('y', 'yes', 't', 'true', 'on', '1'):
        return True
    elif val in ('n', 'no', 'f', 'false', 'off', '0'):
        return False
    else:
        raise ValueError("invalid boolean value env[%r]=%r" % (var, val))


def envlist(var):
    """Returns value of environment variable var split in a comma-separated list.

    Returns an empty list if variable is empty or not set.
    """
    val = [item.strip() for item in os.getenv(var, '').split(',')]
    if val == ['']:
        # "Splitting an empty string with a specified separator returns ['']"
        val = []
    return val


if __name__ == '__main__':
    runtests(test_labels=sys.argv[1:])
