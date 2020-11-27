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
  && pip install -r /requirements/local.txt \
  # cleaning up unused files
  && apt autoremove -y  build-essential python3-dev git \
  && apt purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && rm -rf /var/lib/apt/lists/*

RUN update-alternatives --install /usr/bin/python python /usr/bin/python3 10

COPY ./compose/local/django/entrypoint /entrypoint
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
EXPOSE 8000

ENTRYPOINT ["/entrypoint"]
