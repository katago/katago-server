FROM nginx:stable

# nginx docker image already defines an "nginx" user, we just need to grant
# permissions for a few things to make it work
RUN touch /var/run/nginx.pid && \
  chown -R nginx:nginx /var/run/nginx.pid && \
  chown -R nginx:nginx /var/cache/nginx && \
  chown -R nginx:nginx /var/log/nginx && \
  chown -R nginx:nginx /etc/nginx/conf.d

USER nginx
