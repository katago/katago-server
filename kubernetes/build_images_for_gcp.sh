#!/bin/bash -eux

IMAGEREPOPATH=$(cat imagerepopath.txt | tr -d '\n')
IMAGETAG=$(git describe --abbrev=7 --tags --always --first-parent)

docker build \
       -t "$IMAGEREPOPATH"/katago-django:"$IMAGETAG" \
       -t "$IMAGEREPOPATH"/katago-training-server/katago-django:latest \
       . \
       -f compose/production/django/Dockerfile

docker build \
       -t "$IMAGEREPOPATH"/katago-nginx:"$IMAGETAG" \
       -t "$IMAGEREPOPATH"/katago-nginx:latest \
       . \
       -f compose/production/nginx/Dockerfile

echo "$IMAGETAG"
