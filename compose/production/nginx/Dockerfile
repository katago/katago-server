FROM nginx:stable

COPY ./compose/production/nginx/nginx.conf.template /etc/nginx/nginx.conf.template
COPY ./compose/production/nginx/default.conf.template /etc/nginx/conf.d/default.conf.template
COPY ./compose/production/nginx/defaultnoratelimit.conf.template /etc/nginx/conf.d/defaultnoratelimit.conf.template
COPY ./compose/production/nginx/make_nginx_conf.sh /make_nginx_conf.sh
RUN chmod u+x /make_nginx_conf.sh && chown nginx:nginx /make_nginx_conf.sh
RUN rm -f /etc/nginx/nginx.conf && rm -f /etc/nginx/conf.d/default.conf && touch /etc/nginx/nginx.conf && touch /etc/nginx/conf.d/default.conf

# nginx docker image already defines an "nginx" user, we just need to grant
# permissions for a few things to make it work
RUN touch /var/run/nginx.pid && \
  chown -R nginx:nginx /var/run/nginx.pid && \
  chown -R nginx:nginx /var/cache/nginx && \
  chown -R nginx:nginx /var/log/nginx && \
  chown -R nginx:nginx /etc/nginx/nginx.conf && \
  chown -R nginx:nginx /etc/nginx/conf.d

USER nginx

ENTRYPOINT []