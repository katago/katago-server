#!/bin/bash -eux

gcloud compute ssl-policies create katago-ssl-policy-modern \
    --profile=MODERN \
    --min-tls-version=1.2 \
    --description="SSL policy for katago distributed training website"

