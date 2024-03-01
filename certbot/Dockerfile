FROM certbot/certbot:latest

COPY certbot/check-certs.sh /check-certs.sh

ARG SSL_DOMAIN
ENV DOMAIN=${SSL_DOMAIN}
ENTRYPOINT ["/check-certs.sh"]