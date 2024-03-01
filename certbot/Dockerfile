FROM certbot/certbot:latest

COPY certbot/check-certs.sh /check-certs.sh

# TODO(mfleming) remove me
ENV DOMAIN=staging.nyrkio.com
ENTRYPOINT ["/check-certs.sh"]