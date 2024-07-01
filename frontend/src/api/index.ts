import { BACKEND_PRIVATE_URL } from "../config";
import { HTTPException } from "../lib/http";
import { client } from "./generated/sdk.gen";

client.setConfig({
  baseUrl: BACKEND_PRIVATE_URL,
});

client.interceptors.response.use((response) => {
  if (response.status === 404) {
    throw new HTTPException(404);
  }

  return response;
});

export * from "./generated/sdk.gen";
export * from "./generated/types.gen";
