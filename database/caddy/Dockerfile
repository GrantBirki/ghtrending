FROM caddy/caddy:2.6.1-alpine

# Add curl for healthchecks
RUN apk add curl

RUN mkdir /app
COPY start.sh /app/start.sh

COPY Caddyfile /etc/caddy/Caddyfile

CMD ["sh", "/app/start.sh"]
