# Stage 1: download and build the webpages
FROM python:3.9-slim AS python-build
COPY . .
RUN pip install Jinja2 requests \
 && python3 download_repos.py \
 && python3 -u update.py

# Stage 2: install dependencies and build assets
FROM node:18 AS node-build
ENV NODE_OPTIONS=--openssl-legacy-provider
COPY . .
RUN yarn && yarn build

# Stage 3: host 
FROM debian:bullseye-slim
RUN apt-get update && \
   apt-get install -y apache2 && \
   rm -rf /var/lib/apt/lists/* && \
   echo 'Alias /en /var/www/html/en' >> /etc/apache2/apache2.conf && \
   echo 'Alias /nl /var/www/html/nl' >> /etc/apache2/apache2.conf && \
   echo '<LocationMatch "^/$">' >> /etc/apache2/apache2.conf && \
   echo '    Require all denied' >> /etc/apache2/apache2.conf && \
   echo '</LocationMatch>'  >> /etc/apache2/apache2.conf
COPY --from=python-build /en/ /var/www/html/en/
COPY --from=python-build /nl/ /var/www/html/nl/
COPY --from=python-build /repos/ /var/www/html/repos/
COPY --from=python-build index.json /var/www/html/
COPY --from=node-build /script.js /var/www/html/
COPY style.css logo.svg /var/www/html/
EXPOSE 80
CMD ["apache2ctl", "-D", "FOREGROUND"]