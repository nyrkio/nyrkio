FROM node:20 AS build

WORKDIR /app
COPY frontend/package*.json ./
RUN npm -v
RUN node -v
RUN npm install
COPY frontend/. ./
RUN npm run build

# production env
FROM nginx:1.25
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx/static/ /usr/share/nginx/html
COPY p/ /usr/share/nginx/html/p
EXPOSE 80
EXPOSE 443
RUN rm /etc/nginx/conf.d/default.conf
COPY nginx/nginx.conf /etc/nginx/conf.d/nginx.conf.template
# nyrkio.com or staging.nyrkio.com
ARG DOMAIN
ENV DOMAIN=$DOMAIN
# UI subdomain (e.g. ui-staging.nyrkio.com) — optional
ARG UI_DOMAIN
ENV UI_DOMAIN=$UI_DOMAIN
RUN envsubst '$DOMAIN $UI_DOMAIN' < /etc/nginx/conf.d/nginx.conf.template > /etc/nginx/conf.d/nginx.conf
RUN cat /etc/nginx/conf.d/nginx.conf

RUN mkdir -p /etc/nginx/ssl/live/$DOMAIN/
COPY nyrkio_com_chain.crt /etc/nginx/ssl/live/$DOMAIN/fullchain.crt
COPY nyrkio.com.key       /etc/nginx/ssl/live/$DOMAIN/privkey.key

# UI subdomain SSL certs
RUN mkdir -p /etc/nginx/ssl/live/$UI_DOMAIN/
COPY ui_fullchain.crt /etc/nginx/ssl/live/$UI_DOMAIN/fullchain.crt
COPY ui_privkey.key /etc/nginx/ssl/live/$UI_DOMAIN/privkey.key
