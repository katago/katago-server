katago-server
=============

Collaborative server for Katago

.. image:: https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg
     :target: https://github.com/pydanny/cookiecutter-django/
     :alt: Built with Cookiecutter Django
.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
     :target: https://github.com/ambv/black
     :alt: Black code style


:License: MIT

Installation and Setup
--------
After setting up KataGo you should do the following steps on Ubuntu:

    sudo apt install docker docker-compose

    sudo systemctl enable docker

    sudo usermod -aG docker INSERT_YOUR_USERNAME

then reboot

Starting/Stopping Docker (for a Local Test Server)
--------

     docker-compose -f local.yml build

     docker-compose -f local.yml up  # start up and output logs to current shel

     docker-compose -f local.yml up -d  # daemonize rather than attaching to the current shell

To stop it, ctrl-c. Or if it was started daemonized or you want to stop it from another shell:

     docker-compose -f local.yml down

You should be able to see your server in a browser from something like http://localhost:3000

Running the tests (for a Local Test Server)
--------

Using the local server you set up, this command will run some tests:

     docker-compose -f local.yml run --rm django pytest -vv

Or you can do this if you also want to print stdout as well in each test, which can be useful for debugging a test itself:

     docker-compose -f local.yml run --rm django pytest -vvs


Create an initial admin user for the website
--------

    docker-compose -f local.yml run --rm django python manage.py createsuperuser

Once you have an initial admin user, you should be able to visit http://localhost:3000/admin
and create a Run and create an initial random network for the run (or a non-random network,
if you want to start with a network trained from elsewhere).

You will also want to immediately create periodic jobs for updating the bayesian Elo, for
refreshing the materialized views that store stats about uploaded games and data, setting them
to run every few minutes.


Connecting KataGo to the local server
--------

Once you've put in the necessary configs into the Run and set up the first network through the
admin panel, you should be able to connect the distributed KataGo client to it (`katago contribute`) specifying
http://localhost:3000 as the url of the server and have it work.

The distributed KataGo client can be built from the "distributed" branch of https://github.com/lightvector/KataGo/ or
once it is released you can also download a prebuilt binary.


Getting a shell inside a container
--------
If you want to get "inside" a container and actually have a running interactive shell there to be able to inspect things, run commands, etc,
try this, depending on which container (django, nginx, etc) you want to get a shell inside:

   docker-compose -f local.yml run --rm django bash
   docker-compose -f local.yml run --rm postgres bash
   docker-compose -f local.yml run --rm nginx bash


Accessing the raw database
--------
If you want to get direct raw access to the database to run raw postgres queries an inspect the tables that django has set
up, then you can do something like this:

     docker exec -it NAME_OF_POSTGRES_CONTAINER psql -U DATABASE_USER_NAME -d katago_server_db

You can run "docker container list" to see the containers that you have running, and fill in the appropriate name or id in this command line, and also unless you changed it, the user name for a local server database is hardcoded to "debug", so you might have something like:

     docker exec -it server_postgres_1 psql -U debug -d katago_server_db

Migrations
--------
If you change any of the model definitions (Run, TrainingGame, Network, StartPos, etc) or add a new one, you will want to run:

     docker-compose -f local.yml run --rm django python manage.py makemigrations

This will tell django to make a file that will perform the necessary database alterations. Depending on how you set up docker, this
migrations file might be owned by root or something like that because it was created from within docker. You may need to sudo chown the
file to be owned by you. Then, add the file to be tracked under github and commit it along with your changes.

On a local server, migrations should be actually applied the next time you start up the server. But to explicitly and manually do this if you want:

     docker-compose -f local.yml run --rm django python manage.py migrate


Removing Docker Images and Volumes ("I messed up and want to start over")
--------

Check for images and volumes:

    docker image list

    docker volume list

Then you can prune both lists for unused stuff:

    docker image prune

    docker volume prune

You can directly remove images you don't want:

    docker image rm INSERT_NAME_OF_IMAGE

If you stop all containers and remove *everything* then this should put you back in a clean state to before you built the server or did anything.


Setting up a production server
--------
To set up a production server, you'll need to also:

* Copy ./envs/production_example to envs/production and edit each of those files where it indicates you should fill in an domain name, email, api key, or other parameter for your actual production site. These are the various environment variables that docker compose will expose within all the individual containers for django, postgres, etc, which those containers' main process (django process, postgres database process, etc) will use to configure themselves.

* Copy ./env_example to ./.env and edit the few environment variables within similarly. It must be named ".env" - this is the name of the file that docker-compose attempts to read upon startup to grab extra environment variables out of, which are used in the docker-compose file itself.

* In the process, you'll need to own an actual domain name with nameservers pointed appropriately to the box that this server will run on, sign up for mailgun and sentry and a few other recommended monitoring services for the website, and such.


On a production server to pick up code changes, you will need to rerun:

     docker-compose -f production.yml build

And also if there are migrations, you will need to run this to actually apply the migrations to the production database:

     docker-compose -f production.yml run --rm django python manage.py migrate

Be a little careful about whether the site should stay up or be taken down while the database is migrated. For a local server,
these steps happen automatically simply when you "up" the server, but for prod, they must be done explicitly.


Helpful links
--------

* Docker: https://docs.docker.com/get-started/overview/
* Docker compose: https://docs.docker.com/compose/compose-file/
* Django server settings: http://cookiecutter-django.readthedocs.io/en/latest/settings.html
* Django model fields for defining models and the backend: https://docs.djangoproject.com/en/3.1/ref/models/fields/
* Django queryset API for accessing db within django: https://docs.djangoproject.com/en/3.1/ref/models/querysets/
* Django template language for frontend: https://docs.djangoproject.com/en/3.1/ref/templates/
* Postgres SQL language reference: https://www.postgresql.org/docs/12/queries.html
* Traefik: https://doc.traefik.io/traefik/getting-started/configuration-overview/
* Django cookiecutter docker: http://cookiecutter-django.readthedocs.io/en/latest/deployment-with-docker.html
* CSS reloading and SASS: http://cookiecutter-django.readthedocs.io/en/latest/live-reloading-and-sass-compilation.html


Email Server
^^^^^^^^^^^^
lightvector: This bit is leftover from the django cookiecutter readme, I'm not sure how relevant it is with all the docker containers in the way, but it sounds maybe like a useful thing to be able to do when testing, modulo the fact that there's potentially a docker container layer in between that you have to work through?.

     In development, it is often nice to be able to see emails that are being sent from your application. For that reason local SMTP server `MailHog`_ with a web interface is available as docker container.

     Container mailhog will start automatically when you will run all docker containers.
     Please check `cookiecutter-django Docker documentation`_ for more details how to start all containers.

     With MailHog running, to view messages that are sent by your application, open your browser and go to ``http://127.0.0.1:8025``

     .. _mailhog: https://github.com/mailhog/MailHog



