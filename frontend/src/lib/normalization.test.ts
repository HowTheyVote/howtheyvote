import { strict as assert } from "node:assert";
import { describe, it } from "node:test";
import { normalize } from "./normalization";

describe("normalize", () => {
  it("removes decomposable diacritics", () => {
    assert.strictEqual(normalize("äàáâãå"), "aaaaaa");
    assert.strictEqual(normalize("ÄÀÁÂÃÅ"), "aaaaaa");
  });

  it("remove non-decomposable diacritics", () => {
    assert.strictEqual(normalize("æÆ"), "aeae");
    assert.strictEqual(normalize("œŒ"), "oeoe");
    assert.strictEqual(normalize("øØ"), "oeoe");
    assert.strictEqual(normalize("ßẞ"), "ssss");
    assert.strictEqual(normalize("łŁ"), "ll");
  });
});
