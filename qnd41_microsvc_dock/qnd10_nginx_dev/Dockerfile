FROM nginxinc/nginx-unprivileged:1.24.0-alpine-slim
LABEL maintainer="smartquail.io"

#COPY ./ssl/qnode41_app.crt /etc/nginx/ssl/qnode0_app.crt
#COPY ./ssl/qnode0_app.key /etc/nginx/ssl/qnode0_app.key
COPY ./default.conf.tpl /etc/nginx/default.conf.tpl
COPY ./uwsgi_params /etc/nginx/uwsgi_params
COPY ./run.sh /run.sh


ENV LISTEN_PORT=80
ENV NGINX_PROXY=http://qnd10app:9000
ENV APP_HOST=qnd10app
ENV APP_PORT=9000

USER root

RUN mkdir -p /qnd10app/qnd10app/qnd10app/staticfiles && \
    chmod 755 /qnd10app/qnd10app/qnd10app/staticfiles && \
    mkdir -p /qnd10app/qnd10app/qnd10app/media && \
    chmod 755 /qnd10app/qnd10app/qnd10app/media && \
    mkdir -p /qnd10app/qnd10app/qnd10app/static && \
    chmod 755 /qnd10app/qnd10app/qnd10app/static && \

    touch /etc/nginx/conf.d/default.conf && \
    chown nginx:nginx /etc/nginx/conf.d/default.conf && \
    chmod +x /run.sh

VOLUME /qnd10app/qnd10app/qnd10app/staticfiles
VOLUME /qnd10app/qnd10app/qnd10app/mediafiles
VOLUME /qnd10app/qnd10app/qnd10app/static

USER nginx
#ENTRYPOINT [ "/entrypoint.sh" ]
CMD ["/run.sh"]