FROM node:20 as build

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
EXPOSE 80
EXPOSE 443
RUN rm /etc/nginx/conf.d/default.conf
COPY nginx/nginx.conf /etc/nginx/conf.d/nginx.conf.template
# nyrkio.com or staging.nyrkio.com
ARG DOMAIN
ENV DOMAIN=$DOMAIN
RUN envsubst '$DOMAIN' < /etc/nginx/conf.d/nginx.conf.template > /etc/nginx/conf.d/nginx.conf
RUN cat /etc/nginx/conf.d/nginx.conf

RUN mkdir -p /etc/nginx/ssl/live/$DOMAIN/
COPY nyrkio_com_chain.crt /etc/nginx/ssl/live/$DOMAIN/fullchain.crt
COPY nyrkio_com.key       /etc/nginx/ssl/live/$DOMAIN/privkey.key
