#!/bin/bash -eux

IMAGEREPOPATH=$(cat imagerepopath.txt | tr -d '\n')

docker push "$IMAGEREPOPATH"/katago-django:$(git describe --abbrev=7 --tags --always --first-parent)
docker push "$IMAGEREPOPATH"/katago-django:latest

docker push "$IMAGEREPOPATH"/katago-nginx:$(git describe --abbrev=7 --tags --always --first-parent)
docker push "$IMAGEREPOPATH"/katago-nginx:latest

