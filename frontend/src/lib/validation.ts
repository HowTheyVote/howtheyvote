export function oneOf<T extends readonly string[], F extends string>(
  value: string,
  allowed: T,
  fallback: F,
): T[number] | F;
export function oneOf<T extends readonly string[]>(
  value: string,
  allowed: T,
): T[number] | null;
export function oneOf<T extends readonly string[]>(
  value: string,
  allowed: T,
  fallback?: string,
) {
  if (!allowed.includes(value)) {
    return fallback || null;
  }

  return value;
}
