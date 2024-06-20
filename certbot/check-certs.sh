#!/bin/sh
# Copyright (c) 2024, Nyrkiö Oy

# Handle the chicken and egg problem of having to create certificates before
# nginx will run which can't happen unless nginx is running.
#
# Create dummy certificates if no certificates are found, and replace dummy
# certs with real ones. The user is responsible for running this script like
# so,
#
# 1. check-certs.sh (creates dummy certs)
# 2. Start nginx
# 3. check-certs.sh (replaces dummy certs with real ones)
#
# This allows us to avoid rewriting the nginx configuration until the real
# certificates are available.

if [ -z "$DOMAIN" ]; then
  echo "DOMAIN environment variable is not set"
  exit 1
fi

if [ ! -f /etc/letsencrypt/live/$DOMAIN/fullchain.pem ]; then
  echo "Creating dummy certificate for $DOMAIN"
  mkdir -p /etc/letsencrypt/live/$DOMAIN
  openssl req -x509 -nodes -newkey rsa:2048 -days 1\
    -keyout "/etc/letsencrypt/live/$DOMAIN/privkey.pem" \
    -out "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" \
    -subj "/CN=localhost"
else
  # If the certificate common name (CN) is localhost then that's a dummy certificate
  # and we need to use certbot to create a real one.
  # Alternatively, if the certificate is about to expire in less than 14 days, we should renew it.
  if [ "$(openssl x509 -noout -subject -in /etc/letsencrypt/live/$DOMAIN/fullchain.pem)" = "subject=CN = localhost" ]; then
    echo "Creating real certificate for $DOMAIN"
    # Avoid "live directory exists for $DOMAIN" error
    rm -fr /etc/letsencrypt/*

    # Check EXTRA_DOMAINS and add them to the certificate
    EXTRAS=""
    if [ ! -z "$EXTRA_DOMAINS" ]; then
      for D in $EXTRA_DOMAINS; do
        EXTRAS="$EXTRAS -d $D"
      done
    fi
    certbot certonly --expand --webroot --webroot-path=/var/www/certbot --cert-name $DOMAIN --email admin@nyrkio.com --agree-tos --no-eff-email -d $DOMAIN $EXTRAS
  elif [ "$(openssl x509 -noout -checkend $((60*60*24*14)) -in /etc/letsencrypt/live/$DOMAIN/fullchain.pem)" = "Certificate will expire" ]; then
    echo "Renewing certificate for $DOMAIN"
    certbot renew --expand --webroot --webroot-path=/var/www/certbot --email admin@nyrkio.com --agree-tos --no-eff-email --force-renewal
  else
    echo "Certificate for $DOMAIN already exists and is not a dummy certificate."
  fi
fi

exit 0
