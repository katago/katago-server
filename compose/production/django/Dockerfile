# Python build stage
FROM python:3.8-buster

ENV PYTHONUNBUFFERED 1

RUN apt-get update \
  # psycopg2 dependencies
  && apt-get install -y libpq-dev \
  # MIME magic
  && apt-get install -y libmagic-dev \
  # Translations dependencies
  && apt-get install -y gettext \
  # Let DBshell works
  && apt-get install -y postgresql \
  # cleaning up unused files
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && rm -rf /var/lib/apt/lists/*

RUN addgroup --gid 23460 django \
    && adduser --uid 23450 --ingroup django --disabled-password --gecos "" django

# Requirements are installed here to ensure they will be cached.
COPY ./requirements /requirements
RUN pip install --no-cache-dir -r /requirements/production.txt \
    && rm -rf /requirements

COPY --chown=django:django ./compose/production/django/entrypoint /entrypoint
RUN sed -i 's/\r$//g' /entrypoint
RUN chmod +x /entrypoint

COPY --chown=django:django ./compose/production/django/start /start
RUN sed -i 's/\r$//g' /start
RUN chmod +x /start

COPY --chown=django:django ./compose/production/django/celery/worker/start /start-celeryworker
RUN sed -i 's/\r$//g' /start-celeryworker
RUN chmod +x /start-celeryworker

COPY --chown=django:django ./compose/production/django/celery/beat/start /start-celerybeat
RUN sed -i 's/\r$//g' /start-celerybeat
RUN chmod +x /start-celerybeat

COPY ./compose/production/django/celery/flower/start /start-flower
RUN sed -i 's/\r$//g' /start-flower
RUN chmod +x /start-flower

RUN mkdir -p /data/games
RUN mkdir -p /data/training_npz
RUN mkdir -p /data/networks
RUN chown -R django /data

COPY ./.credentials /.credentials

WORKDIR /app
COPY --chown=django:django . /app

USER django

ENTRYPOINT ["/entrypoint"]
