#!/bin/bash -eux

if [ "$#" -ne 1 ]
then
    echo "USAGE: $0 DESCRPTION"
fi

DESC="$1"
shift

(
    cd kubernetes
    helm upgrade katago-server katago-server --values katago-server/values_private.yaml --cleanup-on-fail --history-max 30 --description "$DESC"
)
