import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";

function computeFileHash(path: string): string {
  const hash = createHash("shake256", { outputLength: 8 });
  const data = readFileSync(path);
  return hash.update(data).digest("hex");
}

const FILE_HASH_CACHE = new Map();

export function assetUrl(path: string): string {
  const normalizedPath = path.replace(/^\//, "");

  const absolutePath = resolve("/howtheyvote/frontend/", normalizedPath);
  let hash = FILE_HASH_CACHE.get(absolutePath);

  if (!hash) {
    hash = computeFileHash(absolutePath);
    FILE_HASH_CACHE.set(absolutePath, hash);
  }

  return `/${normalizedPath}?v=${hash}`;
}
