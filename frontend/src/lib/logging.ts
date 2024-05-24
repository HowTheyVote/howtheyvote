import pino from "pino";

export function getLogger() {
  return pino({
    base: undefined, // Disable inclusion of default `pid` and `hostname` fields
  });
}
