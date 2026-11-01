FROM caddy:2.11.6-builder-alpine AS builder

RUN xcaddy build \
    --with github.com/mholt/caddy-ratelimit

FROM caddy:2.11.6-alpine

COPY --from=builder /usr/bin/caddy /usr/bin/caddy
