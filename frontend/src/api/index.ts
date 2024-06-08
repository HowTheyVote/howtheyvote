import { BACKEND_PRIVATE_URL } from "../config";
import { ApiClient } from "./generated";

export * from "./generated/models";

export const api = new ApiClient({ BASE: BACKEND_PRIVATE_URL });
