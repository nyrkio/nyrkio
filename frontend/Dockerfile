# nyrkio/frontend: the v2 SPA, caddy/static and p/ (nyrkio-proprietary) behind a plain-HTTP Caddy.
# Build context is the repo root, with nyrkio-proprietary checked out at p/ (see .github/workflows/build.yml).
FROM node:20 AS build

WORKDIR /app
COPY frontend/package*.json ./
RUN npm install
COPY frontend/. ./
RUN npm run build

FROM caddy:2-alpine
COPY --from=build /app/dist /usr/share/caddy
COPY caddy/static/ /usr/share/caddy
COPY p/ /usr/share/caddy/p
COPY frontend/Caddyfile /etc/caddy/Caddyfile
EXPOSE 80
