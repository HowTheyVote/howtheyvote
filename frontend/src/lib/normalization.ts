const TRANSLITERATION = {
  "\u00E6": "ae",
  "\u0153": "oe",
  "\u00F8": "oe",
  "\u00DF": "ss",
  "\u0142": "l",
};

export function normalize(string: string): string {
  let normalized = string.toLowerCase();

  // Some characters cannot be properly decomposed so they need to be manually
  // transliterated. We only do this for a few characters that a re common in EU
  // member state languages.
  // See https://www.unicode.org/versions/Unicode15.0.0/ch02.pdf#page=57
  for (const [character, replacement] of Object.entries(TRANSLITERATION)) {
    normalized = normalized.replace(new RegExp(character, "g"), replacement);
  }

  // Normalize decomposable characters by decomposing them first, then removing
  // characters from the diacritics Unicode block.
  // See https://stackoverflow.com/a/37511463
  normalized = normalized.normalize("NFKD").replace(/[\u0300-\u036f]/gu, "");

  return normalized;
}
