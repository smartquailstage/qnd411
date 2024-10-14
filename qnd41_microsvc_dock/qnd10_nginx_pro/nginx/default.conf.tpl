upstream django {
    # server unix:///path/to/your/mysite/mysite.sock; # for a file socket
    server qnd41app:9000; # for a web port socket (we'll use this first)
}


server {
    listen       ${LISTEN_PORT};
    server_name  www.${DOMAIN} 137.184.0.57;

    location /.well-known/acme-challenge/ {
        root /vol/www/;
    }

    location /static {
    alias /qnd41app/qnd41app/qnd41app/static;
    client_max_body_size    1000M;
     }

    location /media {
    alias /qnd41app/qnd41app/qnd41app/media;
    client_max_body_size    1000M;
     }

    location / {
        return 301 https://$host$request_uri;
    }
}