import type { Request } from "@tinyhttp/app";
import { PUBLIC_URL } from "../config";

export function requestReferrerHeader(request: Request) {
  const referrer = request.headers.referer;

  if (!referrer) {
    return null;
  }

  try {
    return new URL(referrer).hostname;
  } catch {
    return null;
  }
}

export function requestReferrerUrlParam(request: Request) {
  return new URL(request.url, PUBLIC_URL).searchParams.get("utm_source");
}
