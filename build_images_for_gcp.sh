#!/bin/bash -eux

IMAGEREPOPATH=$(cat imagerepopath.txt | tr -d '\n')

docker build \
       -t "$IMAGEREPOPATH"/katago-django:$(git describe --abbrev=7 --tags --always --first-parent) \
       -t "$IMAGEREPOPATH"/katago-training-server/katago-django:latest \
       . \
       -f compose/production/django/Dockerfile

docker build \
       -t "$IMAGEREPOPATH"/katago-nginx:$(git describe --abbrev=7 --tags --always --first-parent) \
       -t "$IMAGEREPOPATH"/katago-nginx:latest \
       . \
       -f compose/production/nginx/Dockerfile

