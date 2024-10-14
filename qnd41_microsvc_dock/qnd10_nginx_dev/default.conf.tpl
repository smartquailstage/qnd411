upstream django {
    # server unix:///path/to/your/mysite/mysite.sock; # for a file socket
    server qnd10app:9000; # for a web port socket (we'll use this first)
}

server {
    listen ${LISTEN_PORT};
    server_name 127.0.0.1 localhost 164.90.153.177;

    location /static {
        alias /qnd10app/qnd10app/qnd10app/static;
        client_max_body_size 1000M;
    }

    location /media {
        alias /qnd10app/qnd10app/qnd10app/media;
        client_max_body_size 1000M;
    }

    location /staticfiles {
        alias /qnd10app/qnd10app/qnd10app/staticfiles;
        client_max_body_size 1000M;
    }

    location / {
        uwsgi_pass qnd10app:9000;
        include /etc/nginx/uwsgi_params;
        client_max_body_size 1000M;
    }
}

