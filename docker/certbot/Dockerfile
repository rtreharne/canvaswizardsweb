# FROM certbot/certbot:v1.27.0
FROM certbot/certbot:latest

COPY certify-init.sh /opt/
RUN chmod +x /opt/certify-init.sh

ENTRYPOINT []
CMD ["certbot", "renew"]