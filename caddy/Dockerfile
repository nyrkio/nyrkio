FROM node:20 AS build

WORKDIR /app
COPY frontend/package*.json ./
RUN npm -v
RUN node -v
RUN npm install
COPY frontend/. ./
RUN npm run build

# production env
FROM caddy:2-alpine
COPY --from=build /app/dist /usr/share/caddy
COPY caddy/static/ /usr/share/caddy
COPY p/ /usr/share/caddy/p
EXPOSE 80
EXPOSE 443
# DOMAIN, UI_DOMAIN and UI_BASIC_AUTH_HASH are supplied at runtime (compose.yml)
COPY caddy/Caddyfile /etc/caddy/Caddyfile
COPY nyrkio_com_chain.crt /etc/caddy/ssl/fullchain.crt
COPY nyrkio.com.key       /etc/caddy/ssl/privkey.key
