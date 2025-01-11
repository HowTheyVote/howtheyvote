import { defineConfig, defaultPlugins } from "@hey-api/openapi-ts";

export default defineConfig({
  client: "@hey-api/client-fetch",
  input: "http://backend:5000/api",
  output: "./src/api/generated",
  plugins: [
    ...defaultPlugins,
    {
      name: "@hey-api/sdk",
      throwOnError: true,
    },
  ],
});
