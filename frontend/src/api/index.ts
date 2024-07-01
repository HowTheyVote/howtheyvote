import { createClient } from "@hey-api/client-fetch";
import { BACKEND_PRIVATE_URL } from "../config";
import { HTTPException } from "../lib/http";

const { interceptors } = createClient({
  baseUrl: BACKEND_PRIVATE_URL,
});

interceptors.response.use((response) => {
  if (response.status === 404) {
    throw new HTTPException(404);
  }

  return response;
});

export * from "./generated/services.gen";
export * from "./generated/types.gen";
