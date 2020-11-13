#!/bin/bash

cat /etc/nginx/nginx.conf.template | envsubst -v '${NGINX_REAL_IPS} ${NGINX_REAL_IP_HEADER}' > /etc/nginx/nginx.conf
cat /etc/nginx/conf.d/default.conf.template | envsubst -v '${NGINX_REAL_IPS} ${NGINX_REAL_IP_HEADER}' > /etc/nginx/conf.d/default.conf

exec "$@"
