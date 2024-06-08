FROM node:20-alpine3.19 as dev

WORKDIR /howtheyvote/frontend

RUN apk add make bash

# File watcher for development
RUN apk add entr

COPY package.json package.json
COPY package-lock.json package-lock.json
RUN npm ci

COPY . .
RUN make build

CMD node dist/server.entry.mjs
