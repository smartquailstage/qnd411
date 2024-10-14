upstream django {
    # server unix:///path/to/your/mysite/mysite.sock; # for a file socket
    server qnd41app:9000; # for a web port socket (we'll use this first)
}



server {
    listen         443 ssl;
    server_name    www.${DOMAIN} 137.184.0.57;

    ssl_certificate     /etc/letsencrypt/live/www.${DOMAIN}/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/www.${DOMAIN}/privkey.pem;

    include     /etc/nginx/options-ssl-nginx.conf;

    ssl_dhparam /vol/proxy/ssl-dhparams.pem;

    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;


    location /staticfiles {
        alias /qnd41app/qnd41app/qnd41app/staticfiles;
        client_max_body_size    1000M;
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
        uwsgi_pass qnd41app:9000;
        add_header 'Access-Control-Allow-Origin' 'https://www.smartquail.io';
        add_header Access-Control-Allow-Methods "GET, POST, OPTIONS";
        add_header Access-Control-Allow-Headers "Authorization, Content-Type, Accept";
        add_header Access-Control-Allow-Credentials "true";
        proxy_set_header X-Forwarded-Proto https;
        include /etc/nginx/uwsgi_params;
        client_max_body_size 1000M;
    }
}