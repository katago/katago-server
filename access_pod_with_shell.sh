#!/bin/bash -eux

if [ "$#" -ne 1 ]
then
    echo "USAGE: $0 PODNAME"
fi

PODNAME="$1"
shift

if [[ "$PODNAME" == *"nginx"* ]]
then
    kubectl exec --stdin --tty "$PODNAME" -- /bin/bash
else
    kubectl exec --stdin --tty "$PODNAME" -- /entrypoint /bin/bash
fi
