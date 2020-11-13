#!/bin/bash -eu

if [ "${NGINX_DO_RATE_LIMIT}" -eq "1" ]
then
    cat /etc/nginx/nginx.conf.template | envsubst '${NGINX_TRUSTED_IP_PROXY_LIST} ${NGINX_REAL_IP_HEADER}' > /etc/nginx/nginx.conf
    cat /etc/nginx/conf.d/default.conf.template | envsubst '${NGINX_TRUSTED_IP_PROXY_LIST} ${NGINX_REAL_IP_HEADER}' > /etc/nginx/conf.d/default.conf
else
    cat /etc/nginx/nginx.conf.template | envsubst '${NGINX_TRUSTED_IP_PROXY_LIST} ${NGINX_REAL_IP_HEADER}' > /etc/nginx/nginx.conf
    cat /etc/nginx/conf.d/defaultnoratelimit.conf.template | envsubst '${NGINX_TRUSTED_IP_PROXY_LIST} ${NGINX_REAL_IP_HEADER}' > /etc/nginx/conf.d/defaultnoratelimit.conf
fi

exec "$@"
