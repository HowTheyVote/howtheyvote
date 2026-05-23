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
];

export function requestIsBot(
  path: string,
  userAgent?: string,
): {
  result: boolean;
  name?: string;
} {
  // Detect certain bots based on user agent
  const match = isbotMatch(userAgent);

  if (match) {
    return {
      result: true,
      name: match,
    };
  }

  // Detect bots based on common request patterns
  for (const prefix of BOT_PATH_PREFIXES) {
    if (path.startsWith(prefix)) {
      return { result: true };
    }
  }

  for (const suffix of BOT_PATH_SUFFXIES) {
    if (path.endsWith(suffix)) {
      return { result: true };
    }
  }

  return { result: false };
}
