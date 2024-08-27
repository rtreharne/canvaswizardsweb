server {
    listen 80;
    server_name www.canvaswizards.org.uk;

    location /.well-known/acme-challenge/ {
        root /vol/www/;
    }

    location / {
        return 301 https://canvaswizards.org.uk$request_uri;
    }
}

server {
    listen 443 ssl;
    server_name www.canvaswizards.org.uk;

    ssl_certificate /etc/letsencrypt/live/canvaswizards.org.uk/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/canvaswizards.org.uk/privkey.pem;

    include /etc/nginx/options-ssl-nginx.conf;
    ssl_dhparam /vol/proxy/ssl-dhparams.pem;

    return 301 https://canvaswizards.org.uk$request_uri;
}

server {
    listen 443 ssl;
    server_name canvaswizards.org.uk;

    ssl_certificate /etc/letsencrypt/live/canvaswizards.org.uk/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/canvaswizards.org.uk/privkey.pem;

    include /etc/nginx/options-ssl-nginx.conf;
    ssl_dhparam /vol/proxy/ssl-dhparams.pem;

    location /static {
        alias /vol/static;
    }

    location / {
        uwsgi_pass ${APP_HOST}:${APP_PORT};
        include /etc/nginx/uwsgi_params;
        client_max_body_size 50M;
        uwsgi_param X-Forwarded-Proto https;
    }
}
