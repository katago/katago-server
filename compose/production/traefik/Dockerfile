FROM traefik:2.2.1
RUN mkdir -p /etc/traefik/acme
RUN touch /etc/traefik/acme/acme.json
RUN chmod 600 /etc/traefik/acme/acme.json
COPY ./compose/production/traefik/traefik.toml /etc/traefik
