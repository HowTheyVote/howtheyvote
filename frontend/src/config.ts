export const PUBLIC_URL = getEnv("HTV_FRONTEND_PUBLIC_URL", "");
export const BACKEND_PRIVATE_URL = getEnv("HTV_BACKEND_PRIVATE_URL", "");
export const BACKEND_PUBLIC_URL = getEnv("HTV_BACKEND_PUBLIC_URL", "");
export const TIMEZONE = "Europe/Brussels";
export const CURRENT_TERM_START_DATE = "2024-07-16";
export const GEOLITE2_ASN_PATH = getEnv("HTV_FRONTEND_GEOLITE2_ASN_PATH", "");
export const GEOLITE2_COUNTRY_PATH = getEnv(
  "HTV_FRONTEND_GEOLITE2_COUNTRY_PATH",
  "",
);

function getEnv(name: string): string | undefined;
function getEnv(name: string, defaultValue: string): string;
function getEnv(name: string, defaultValue?: string): string | undefined {
  // `process.env` isn’t available on the client
  if (typeof process === "undefined") {
    return defaultValue;
  }

  return process.env[name] || defaultValue;
}
