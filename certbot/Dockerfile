FROM certbot/certbot:latest

COPY certbot/check-certs.sh /check-certs.sh

#ARG SSL_DOMAIN
ENV SSL_DOMAIN=nyrkio.com
ENV DOMAIN=nyrkio.com
ARG EXTRA_DOMAINS
ENV EXTRA_DOMAINS=${EXTRA_DOMAINS}
ENTRYPOINT ["/check-certs.sh"]
