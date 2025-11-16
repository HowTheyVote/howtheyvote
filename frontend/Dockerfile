FROM node:22-alpine3.21 AS dev

WORKDIR /howtheyvote/frontend

RUN apk add make bash entr

COPY package.json package-lock.json ./
RUN npm ci

COPY . .
RUN make build

CMD ["node", "dist/server.entry.mjs"]
