#/bin/sh

echo "nginx config smoke test"
NGINXDIR=$(pwd)/$(dirname $0)


DOMAIN=example.com envsubst '$DOMAIN' < nginx.conf |grep -v ssl > nginx.conf.test

# Despite -T this will actually attempt to start nginx, then immediately shutdown
# SUDO needed for port 80
sudo nginx -T -c $NGINXDIR/etc_nginx_conf -p $NGINXDIR/nginx

