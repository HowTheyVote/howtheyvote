type Modifiers =
  | boolean
  | undefined
  | null
  | string
  | Array<boolean | undefined | null | string>
  | Record<string, boolean | undefined | null>;

function normalizeModifiers(modifiers: Modifiers) {
  const normalized = [];

  if (!modifiers) {
    return [];
  }

  if (typeof modifiers === "string") {
    return [modifiers];
  }

  if (!Array.isArray(modifiers)) {
    for (const [key, value] of Object.entries(modifiers)) {
      if (typeof key === "string" && value) {
        normalized.push(key);
      }
    }
  }

  if (Array.isArray(modifiers)) {
    for (const value of modifiers) {
      if (typeof value === "string") {
        normalized.push(value);
      }
    }
  }

  return normalized;
}

export function bem(base: string, modifiers: Modifiers) {
  const modifierClasses = normalizeModifiers(modifiers)
    .map((modifier) => `${base}--${modifier}`)
    .join(" ");

  return `${base} ${modifierClasses}`;
}
