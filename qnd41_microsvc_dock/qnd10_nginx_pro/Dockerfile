FROM nginxinc/nginx-unprivileged:1.24.0-alpine-slim

COPY ./nginx/* /etc/nginx/
COPY ./ssl-certs-smartquail/* /etc/nginx/
COPY ./nginx/run.sh /run.sh
COPY ./ssl-certs-smartquail/https/www.smartquail.io/* /etc/letsencrypt/live/www.smartquail.io/
COPY ./ssl-certs-smartquail/https/smartquail.io/* /etc/letsencrypt/live/smartquail.io/


ENV DOMAIN=smartquail.io
ENV LISTEN_PORT=80
ENV NGINX_PROXY=http://qnd41app:9000
ENV APP_HOST=qnd41app
ENV APP_PORT=9000

USER root

RUN apk add --no-cache openssl bash
RUN chmod +x /run.sh

RUN mkdir -p /qnd41app/qnd41app/qnd41app/staticfiles && \
    chmod 755 /qnd41app/qnd41app/qnd41app/staticfiles && \
    mkdir -p /qnd41app/qnd41app/qnd41app/media && \
    chmod 755 /qnd41app/qnd41app/qnd41app/media && \
    mkdir -p /qnd41app/qnd41app/qnd41app/static && \
    chmod 755 /qnd41app/qnd41app/qnd41app/static

VOLUME /qnd41app/qnd41app/qnd41app/staticfiles
VOLUME /qnd41app/qnd41app/qnd41app/mediafiles
VOLUME /qnd41app/qnd41app/static
VOLUME /vol/www
VOLUME /vol/proxy
VOLUME /etc/letsencrypt

CMD ["/run.sh"]