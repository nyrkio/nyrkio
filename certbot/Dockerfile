FROM certbot/certbot:latest

COPY certbot/check-certs.sh /check-certs.sh

ARG SSL_DOMAIN
ENV DOMAIN=${SSL_DOMAIN}
ARG EXTRA_DOMAINS
ENV EXTRA_DOMAINS=${EXTRA_DOMAINS}
ENTRYPOINT ["/check-certs.sh"]