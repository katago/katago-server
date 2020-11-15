# Python build stage
FROM python:3.8-alpine3.12

ENV PYTHONUNBUFFERED 1

RUN apk add --no-cache --virtual build-deps alpine-sdk gfortran python3-dev musl-dev libffi-dev openblas-dev
RUN apk add --no-cache postgresql-dev \
  postgresql-client \
  # MIME magic
  libmagic \
  # Translations dependencies
  gettext

# Requirements are installed here to ensure they will be cached.
COPY ./requirements /requirements
RUN pip install --no-cache-dir -r /requirements/local.txt
RUN apk del build-deps

COPY ./compose/production/django/entrypoint /entrypoint
RUN sed -i 's/\r$//g' /entrypoint
RUN chmod +x /entrypoint

COPY ./compose/local/django/start /start
RUN sed -i 's/\r$//g' /start
RUN chmod +x /start

COPY ./compose/local/django/celery/worker/start /start-celeryworker
RUN sed -i 's/\r$//g' /start-celeryworker
RUN chmod +x /start-celeryworker

COPY ./compose/local/django/celery/beat/start /start-celerybeat
RUN sed -i 's/\r$//g' /start-celerybeat
RUN chmod +x /start-celerybeat

COPY ./compose/local/django/celery/flower/start /start-flower
RUN sed -i 's/\r$//g' /start-flower
RUN chmod +x /start-flower

RUN mkdir /data

WORKDIR /app

ENTRYPOINT ["/entrypoint"]
