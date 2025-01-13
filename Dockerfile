# --- Stage 1 Node build
FROM node:18-slim AS node-build

WORKDIR /app

COPY src ./
COPY webpack.config.js yarn.lock package.json ./

RUN yarn install --frozen-lockfile

ENV NODE_OPTIONS="--openssl-legacy-provider"
COPY . .
RUN yarn build

# --- Stage 2 Python build
FROM python:3.9-slim AS python-build

WORKDIR /app
COPY --from=node-build /app ./

COPY download_repos.py update.py config.json ./
RUN ls -l /app

RUN pip install --no-cache-dir Jinja2 requests && \
    python3 download_repos.py && \
    python3 -u update.py 

# --- Stage 3: Final nginx stage
FROM nginx:stable

COPY nginx.conf /etc/nginx/conf.d/default.conf

COPY --from=python-build /app/en/ /var/www/html/en/
COPY --from=python-build /app/nl/ /var/www/html/nl/
COPY --from=python-build /app/repos/ /var/www/html/repos/
COPY --from=python-build /app/index.json /var/www/html/
COPY --from=node-build /app/script.js /var/www/html/
COPY style.css logo.svg /var/www/html/

RUN chown -R nginx:nginx /var/www/html && \
    chmod -R 755 /var/www/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]