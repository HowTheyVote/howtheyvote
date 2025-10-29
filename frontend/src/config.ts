export const PUBLIC_URL = getEnv("HTV_FRONTEND_PUBLIC_URL", "");
export const BACKEND_PRIVATE_URL = getEnv("HTV_BACKEND_PRIVATE_URL", "");
export const BACKEND_PUBLIC_URL = getEnv("HTV_BACKEND_PUBLIC_URL", "");
export const TIMEZONE = "Europe/Brussels";

function getEnv(name: string): string | undefined;
function getEnv(name: string, defaultValue: string): string;
function getEnv(name: string, defaultValue?: string): string | undefined {
  // `process.env` isn’t available on the client
  if (!process?.env) {
    return defaultValue;
  }

  return process.env[name] || defaultValue;
}
