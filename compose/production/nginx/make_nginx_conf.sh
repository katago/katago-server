#!/bin/bash -eu

cat /etc/nginx/nginx.conf.template | envsubst '${NGINX_TRUSTED_IP_PROXY_LIST} ${NGINX_REAL_IP_HEADER}' > /etc/nginx/nginx.conf
cat /etc/nginx/conf.d/default.conf.template | envsubst '${NGINX_TRUSTED_IP_PROXY_LIST} ${NGINX_REAL_IP_HEADER}' > /etc/nginx/conf.d/default.conf

exec "$@"
