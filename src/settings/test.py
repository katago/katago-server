"""
With these settings, tests run faster.
"""

from .base import *  # noqa
from .base import env

# GENERAL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
SECRET_KEY = env("DJANGO_SECRET_KEY", default="YGYzKmhgOxuSBPafqxgqtTDkcG5zbcb2x7lSNawdqmI8fLIx9W6yuj7V98XBMQIF",)
# https://docs.djangoproject.com/en/dev/ref/settings/#test-runner
TEST_RUNNER = "django.test.runner.DiscoverRunner"

# CACHES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#caches
CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache", "LOCATION": "",}}

# PASSWORDS
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#password-hashers
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

# TEMPLATES
# ------------------------------------------------------------------------------
TEMPLATES[0]["OPTIONS"]["loaders"] = [  # noqa F405
    ("django.template.loaders.cached.Loader", ["django.template.loaders.filesystem.Loader", "django.template.loaders.app_directories.Loader",],)
]

# EMAIL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#email-backend
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# MEDIA
# ------------------------------------------------------------------------------
NETWORK_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"
SGF_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"
NPZ_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"

NETWORK_USE_PROXY_DOWNLOAD = False

# Your stuff...
# ------------------------------------------------------------------------------

# Dummy "site" domain for cookiecutters migration, which populates the "sites" db on the very first migration after
# the site is built with these values, which is used in a production setting for full absolute URL building and
# other such stuff
SITE_DOMAIN_FOR_MIGRATION="example.com"
SITE_NAME_FOR_MIGRATION="example.com"
