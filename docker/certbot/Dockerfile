# Use multi-stage build to support both x86_64 and ARM architectures

# Stage 1: x86_64 architecture (default)
FROM certbot/certbot:v1.27.0 as amd64

# Stage 2: ARM architecture
FROM certbot/certbot:arm32v7-latest as arm

# Copy the certify-init.sh script in both stages
COPY certify-init.sh /opt/
RUN chmod +x /opt/certify-init.sh

# Default stage
FROM ${TARGETARCH}-image as final

CMD ["certbot", "renew"]