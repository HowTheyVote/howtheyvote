import * as Sentry from "@sentry/node";

import { BACKEND_PRIVATE_URL } from "../config";
import { HTTPException } from "../lib/http";
import { client } from "./generated/client.gen";

client.setConfig({
  baseUrl: BACKEND_PRIVATE_URL,
});

client.interceptors.response.use((response) => {
  if (response.status === 404) {
    throw new HTTPException(404);
  }

  return response;
});

client.interceptors.request.use((request) => {
  const traceData = Sentry.getTraceData();

  if (traceData["sentry-trace"] && traceData.baggage) {
    request.headers.set("sentry-trace", traceData["sentry-trace"]);
    request.headers.set("baggage", traceData.baggage);
  }

  return request;
});

export * from "./generated/sdk.gen";
export * from "./generated/types.gen";
