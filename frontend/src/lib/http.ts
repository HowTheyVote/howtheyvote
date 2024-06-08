import type { ParsedUrlQuery } from "node:querystring";

export class HTTPException extends Error {
  code: number;

  constructor(code: number) {
    super(code.toString());
    this.code = code;
  }
}

export class RedirectException extends HTTPException {
  location: string;

  constructor(code: 301 | 302, location: string) {
    super(code);
    this.location = location;
  }
}

export function abort(code: number): never {
  throw new HTTPException(code);
}

export function redirect(location: string, code: 301 | 302 = 301): never {
  throw new RedirectException(code, location);
}

export function firstQueryValue(
  query: ParsedUrlQuery,
  name: string,
): string | undefined {
  const value = query[name];

  if (Array.isArray(value)) {
    return value[0];
  }

  return value;
}
