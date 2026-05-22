import { defineConfig, defaultPlugins } from "@hey-api/openapi-ts";

export default defineConfig({
  input: "http://backend:5000/api",
  output: "./src/api/generated",
  plugins: [
    ...defaultPlugins,
    {
      name: "@hey-api/client-fetch",
      throwOnError: true,
      baseUrl: false,
    },
    {
      name: "@hey-api/sdk",
      operations: {
        strategy: "single",
      },
    },
  ],
});
