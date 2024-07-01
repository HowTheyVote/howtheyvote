default: lint typecheck test

dev:
	./scripts/watch

build: build-server build-client

lint:
	./node_modules/.bin/biome check src static

lint-fix:
	./node_modules/.bin/biome check --write src static

typecheck:
	./node_modules/.bin/tsc --noEmit

typegen:
	./node_modules/.bin/openapi-ts \
		--input http://backend:5000/api \
		--output ./src/api/generated \
		--schemas false \
		--useOptions

test:
	node \
		--import ./src/setupTests.js \
		--import ./src/cssLoader.js \
		--import tsx/esm \
		--test \
		./src/**/*.test.tsx ./src/**/*.test.ts

clean:
	rm -rf ./dist

build-server:
	./node_modules/.bin/esbuild \
		--bundle \
		--platform=node \
		--format=esm \
		--packages=external \
		--external:*jpg \
		--external:*.woff \
		--external:*.woff2 \
		--sourcemap=inline \
		--outfile=dist/server.entry.mjs \
		--keep-names \
		src/server.entry.ts

build-client:
	./node_modules/.bin/esbuild \
		--bundle \
		--external:*.jpg \
		--outfile=dist/client.entry.js \
		--minify \
		--keep-names \
		src/client.entry.ts
