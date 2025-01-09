FROM python:3.9-slim

WORKDIR /

RUN apt-get update && \
    apt-get install -y curl apache2 && \
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs && \
    npm install -g yarn && \
    pip install Jinja2 && \
    pip install requests

ENV NODE_OPTIONS=--openssl-legacy-provider

COPY . .
RUN python3 download_repos.py && \
    python3 -u update.py && \
    test -f index.json && \
    yarn && yarn build && \
    mkdir -p /var/www/html && \
    cp -r /en /var/www/html/ && \
    cp -r /nl /var/www/html/ && \
    cp -r /repos /var/www/html/ && \
    cp style.css /var/www/html/ && \
    cp logo.svg /var/www/html/ && \
    cp script.js /var/www/html/ && \
    cp index.json /var/www/html/

EXPOSE 80

CMD ["apache2ctl", "-D", "FOREGROUND"]
