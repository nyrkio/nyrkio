FROM node:bookworm as build

WORKDIR /app
COPY frontend/package*.json ./
RUN ls -al /app/package.json
RUN npm install
COPY frontend/. ./
RUN npm run build

# production env
FROM nginx:1.25
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
COPY nginx/nginx.conf /etc/nginx/conf.d
CMD ["nginx", "-g", "daemon off;"]