import type { Request } from "@tinyhttp/app";
import { isbotMatch } from "isbot";

const BOT_PATH_PREFIXES = [
  "/.env",
  "/wp",
  "/wordpress",
  "/admin",
  "/login",
  "/xmlrpc",
  "/.git",
  "/old",
  "/new",
  "/backup",
  "/wap",
  "/user",
  "/robots.txt",
  "/cgi-bin",
  "/ipfs",
  "/blog",
  "/ip",
  "/graphql",
  "/signin",
  "/register",
];

const BOT_PATH_SUFFXIES = [
  ".php",
  ".asp",
  ".aspx",
  ".env",
  ".do",
  ".conf",
  ".js",
  ".css",
  ".json",
  ".env",
];

const DEFAULT_HEADERS = ["user-agent", "accept-language", "accept-encoding"];

export function requestIsBot(request: Request): {
  result: boolean;
  name?: string;
} {
  // Detect certain bots based on user agent
  const match = isbotMatch(request.headers["user-agent"]);

  if (match) {
    return {
      result: true,
      name: match,
    };
  }

  // Normalize multiple leading slashes
  const path = request.path.replace(/^\/+/, "/");

  // Detect bots based on common request patterns
  for (const prefix of BOT_PATH_PREFIXES) {
    if (path.startsWith(prefix)) {
      return { result: true };
    }
  }

  for (const suffix of BOT_PATH_SUFFXIES) {
    if (request.path.endsWith(suffix)) {
      return { result: true };
    }
  }

  for (const header of DEFAULT_HEADERS) {
    if (!request.headers[header]) {
      console.log(header, request.headers[header]);
      return { result: true };
    }
  }

  return { result: false };
}
