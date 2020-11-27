FROM ubuntu:20.10

ENV PYTHONUNBUFFERED 1
ENV DEBIAN_FRONTEND=noninteractive

# Requirements are installed here to ensure they will be cached.
COPY ./requirements /requirements

RUN apt update \
    # dependencies for building Python packages
    && apt install -y python3 python3-dev python3-pip \
    # dependencies for building Python packages
    && apt install -y build-essential git \
    # psycopg2 dependencies
    && apt install -y libpq-dev \
    # MIME magic
    && apt install -y libmagic-dev \
    # Translations dependencies
    && apt install -y gettext \
    # Let DBshell works
    && apt install -y postgresql \
    # Install Python deps
    && pip install --no-cache-dir -r /requirements/production.txt \
    # cleaning up unused files
    && apt autoremove -y build-essential python3-dev git \
    && apt purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
    && rm -rf /var/lib/apt/lists/*

RUN update-alternatives --install /usr/bin/python python /usr/bin/python3 10

RUN addgroup --gid 23460 django \
    && adduser --uid 23450 --ingroup django --disabled-password --gecos "" django

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

RUN mkdir -p /data/games \
    && mkdir -p /data/training_npz \
    && mkdir -p /data/networks \
    && chown -R django /data

COPY ./.credentials /.credentials

WORKDIR /app

# staticfiles is for collectstatic in start script, for whitenoise static middleware
# src is all the django python source that django will use
# locale is for i18n

RUN chown django:django /app \
    && mkdir -p /app/staticfiles \
    && chown django:django /app/staticfiles \
    && mkdir -p /app/locale \
    && chown django:django /app/locale \
    && mkdir -p /app/src \
    && chown django:django /app/src

COPY --chown=django:django locale  /app/locale
COPY --chown=django:django src  /app/src
COPY --chown=django:django manage.py  /app

USER django
EXPOSE 5000

ENTRYPOINT ["/entrypoint"]
