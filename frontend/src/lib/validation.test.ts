import { strict as assert } from "node:assert";
import { describe, it } from "node:test";
import { oneOf } from "./validation";

describe("oneOf", () => {
  it("returns value if it is allowed", () => {
    assert.strictEqual(oneOf("foo", ["foo", "bar"]), "foo");
    assert.strictEqual(oneOf("foo", ["foo", "bar"], "bar"), "foo");
  });

  it("returns fallback if value is not allowed", () => {
    assert.strictEqual(oneOf("foo", ["bar", "baz"], "bar"), "bar");
  });

  it("returns null if value is not allowed and no fallback is defined", () => {
    assert.strictEqual(oneOf("foo", ["bar", "baz"]), null);
  });
});
