import logging

import sentry_sdk
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.logging import LoggingIntegration

from .base import *  # noqa
from .base import env

# noinspection PyUnresolvedReferences

# GENERAL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
SECRET_KEY = env("DJANGO_SECRET_KEY")
# https://docs.djangoproject.com/en/dev/ref/settings/#allowed-hosts
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS")
# https://pypi.org/project/django-allow-cidr/
ALLOWED_CIDR_NETS = env.list("DJANGO_ALLOWED_CIDR_NETS", default=[])

# "site" domain for cookiecutters migration, which populates the "sites" db on the very first migration after
# the site is built with these values, which is used in a production setting for full absolute URL building and
# other such stuff.
# See src/contrib/sites/migrations/0003_set_site_domain_and_name.py
SITE_DOMAIN_FOR_MIGRATION = env("DJANGO_SITE_DOMAIN_FOR_MIGRATION")
SITE_NAME_FOR_MIGRATION = env("DJANGO_SITE_NAME_FOR_MIGRATION")

# DATABASES
# ------------------------------------------------------------------------------
DATABASES["default"] = env.db("DATABASE_URL", default="")  # noqa F405
DATABASES["default"]["ATOMIC_REQUESTS"] = True  # noqa F405
DATABASES["default"]["CONN_MAX_AGE"] = env.int("CONN_MAX_AGE", default=60)  # noqa F405

# CACHES
# ------------------------------------------------------------------------------
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": env("REDIS_URL"),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            # Mimicing memcache behavior.
            # http://niwinz.github.io/django-redis/latest/#_memcached_exceptions_behavior
            "IGNORE_EXCEPTIONS": True,
            "PARSER_CLASS": "redis.connection.HiredisParser",
        },
    }
}

# SECURITY
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#secure-proxy-ssl-header
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
# https://docs.djangoproject.com/en/dev/ref/settings/#secure-ssl-redirect
SECURE_SSL_REDIRECT = env.bool("DJANGO_SECURE_SSL_REDIRECT", default=True)
# https://docs.djangoproject.com/en/dev/ref/settings/#session-cookie-secure
SESSION_COOKIE_SECURE = True
# https://docs.djangoproject.com/en/dev/ref/settings/#csrf-cookie-secure
CSRF_COOKIE_SECURE = True
# https://docs.djangoproject.com/en/dev/topics/security/#ssl-https
# https://docs.djangoproject.com/en/dev/ref/settings/#secure-hsts-seconds
SECURE_HSTS_SECONDS = 15552000 if env.bool("DJANGO_SECURE_HSTS_LONG", default=False) else 60
# https://docs.djangoproject.com/en/dev/ref/settings/#secure-hsts-include-subdomains
SECURE_HSTS_INCLUDE_SUBDOMAINS = env.bool("DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS", default=True)
# https://docs.djangoproject.com/en/dev/ref/settings/#secure-hsts-preload
SECURE_HSTS_PRELOAD = env.bool("DJANGO_SECURE_HSTS_PRELOAD", default=True)
# https://docs.djangoproject.com/en/dev/ref/middleware/#x-content-type-options-nosniff
SECURE_CONTENT_TYPE_NOSNIFF = env.bool("DJANGO_SECURE_CONTENT_TYPE_NOSNIFF", default=True)

# STATIC STORAGE
# ------------------------
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# MEDIA STORAGE
# ------------------------------------------------------------------------------

if (
    env.bool("NETWORK_USE_GOOGLE_CLOUD_STORAGE", default=False)
    or env.bool("SGF_USE_GOOGLE_CLOUD_STORAGE", default=False)
    or env.bool("NPZ_USE_GOOGLE_CLOUD_STORAGE", default=False)
):
    GS_BUCKET_NAME = env("DJANGO_GCP_STORAGE_BUCKET_NAME")
    GS_DEFAULT_ACL = "publicRead"
    GS_FILE_OVERWRITE = False
    GS_BLOB_CHUNK_SIZE = 1024 * 1024 * 5  # 5 MB
    GS_CACHE_CONTROL = "no-cache"
    GS_LOCATION = "uploaded/"

NETWORK_USE_PROXY_DOWNLOAD = False
if env.bool("NETWORK_USE_PROXY_DOWNLOAD", default=False):
    NETWORK_USE_PROXY_DOWNLOAD = True
    NETWORK_PROXY_DOWNLOAD_URL_BASE = env("NETWORK_PROXY_DOWNLOAD_URL_BASE")

NETWORK_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"
if env.bool("NETWORK_USE_GOOGLE_CLOUD_STORAGE", default=False):
    NETWORK_FILE_STORAGE = "storages.backends.gcloud.GoogleCloudStorage"

SGF_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"
if env.bool("SGF_USE_GOOGLE_CLOUD_STORAGE", default=False):
    SGF_FILE_STORAGE = "storages.backends.gcloud.GoogleCloudStorage"

NPZ_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"
if env.bool("NPZ_USE_GOOGLE_CLOUD_STORAGE", default=False):
    NPZ_FILE_STORAGE = "storages.backends.gcloud.GoogleCloudStorage"

DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"
MEDIA_ROOT = "/data"
MEDIA_URL = "/media/"


# TEMPLATES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#templates
TEMPLATES[0]["OPTIONS"]["loaders"] = [  # noqa F405
    (
        "django.template.loaders.cached.Loader",
        [
            "django.template.loaders.filesystem.Loader",
            "django.template.loaders.app_directories.Loader",
        ],
    )
]

# EMAIL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#default-from-email
DEFAULT_FROM_EMAIL = env("DJANGO_DEFAULT_FROM_EMAIL")
# https://docs.djangoproject.com/en/dev/ref/settings/#server-email
SERVER_EMAIL = env("DJANGO_SERVER_EMAIL", default=DEFAULT_FROM_EMAIL)
# https://docs.djangoproject.com/en/dev/ref/settings/#email-subject-prefix
EMAIL_SUBJECT_PREFIX = env("DJANGO_EMAIL_SUBJECT_PREFIX", default="[katago-server]")

# ADMIN
# ------------------------------------------------------------------------------
# Django Admin URL regex.
ADMIN_URL = env("DJANGO_ADMIN_URL")

# Anymail (Mailgun)
# ------------------------------------------------------------------------------
# https://anymail.readthedocs.io/en/stable/installation/#installing-anymail
INSTALLED_APPS += ["anymail"]  # noqa F405
EMAIL_BACKEND = "anymail.backends.mailgun.EmailBackend"
# https://anymail.readthedocs.io/en/stable/installation/#anymail-settings-reference
ANYMAIL = {
    "MAILGUN_API_KEY": env("MAILGUN_API_KEY"),
    "MAILGUN_SENDER_DOMAIN": env("MAILGUN_DOMAIN"),
    "MAILGUN_API_URL": env("MAILGUN_API_URL", default="https://api.mailgun.net/v3"),
}

# LOGGING
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#logging
# See https://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.

LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {"verbose": {"format": "%(levelname)s %(asctime)s %(module)s " "%(process)d %(thread)d %(message)s"}},
    "handlers": {"console": {"level": "DEBUG", "class": "logging.StreamHandler", "formatter": "verbose"}},
    "root": {"level": "INFO", "handlers": ["console"]},
    "loggers": {
        "django.db.backends": {"level": "ERROR", "handlers": ["console"], "propagate": False},
        # Errors logged by the SDK itself
        "sentry_sdk": {"level": "ERROR", "handlers": ["console"], "propagate": False},
        "django.security.DisallowedHost": {"level": "ERROR", "handlers": ["console"], "propagate": False},
    },
}

# Sentry
# ------------------------------------------------------------------------------
SENTRY_DSN = env("SENTRY_DSN")
SENTRY_LOG_LEVEL = env.int("DJANGO_SENTRY_LOG_LEVEL", logging.INFO)

sentry_logging = LoggingIntegration(
    level=SENTRY_LOG_LEVEL,  # Capture info and above as breadcrumbs
    event_level=logging.ERROR,  # Send errors as events
)
sentry_sdk.init(
    dsn=SENTRY_DSN,
    integrations=[sentry_logging, DjangoIntegration(), CeleryIntegration()],
)

# Your stuff...
# ------------------------------------------------------------------------------

# Allow for more deletions and creations of things at at time in admin panel
DATA_UPLOAD_MAX_NUMBER_FIELDS = 50000
DATA_UPLOAD_MAX_MEMORY_SIZE = 2500000


# Installed LAST, as recommended by https://github.com/un1t/django-cleanup
INSTALLED_APPS += ["django_cleanup.apps.CleanupConfig"]
