import { strict as assert } from "node:assert";
import { describe, it } from "node:test";
import { getByRole } from "@testing-library/preact";
import userEvent from "@testing-library/user-event";
import renderToString from "preact-render-to-string";
import { useState } from "preact/hooks";
import { Island, hydrateIslands } from "./islands";

function TestComponent({ initialValue = 0 }: { initialValue?: number }) {
  const [count, setCount] = useState(initialValue);

  return (
    <button type="button" onClick={() => setCount(count + 1)}>
      Count {count}
    </button>
  );
}

describe("hydrateIslands", () => {
  it("hydrates islands", async () => {
    // Simulate server rendered component
    document.body.innerHTML = renderToString(
      <Island>
        <TestComponent />
      </Island>,
    );

    const button = getByRole(document.body, "button");

    // Clicking the button doesn't change the state because the
    // island hasn't been hydrated
    assert.strictEqual(button.textContent, "Count 0");
    await userEvent.click(button);
    assert.strictEqual(button.textContent, "Count 0");

    // Now hydrate all islands on the page
    hydrateIslands([TestComponent]);

    // Clicking the button now increases the counter
    assert.strictEqual(button.textContent, "Count 0");
    await userEvent.click(button);
    assert.strictEqual(button.textContent, "Count 1");
  });

  it("hydrates islands with props", async () => {
    document.body.innerHTML = renderToString(
      <Island>
        <TestComponent initialValue={10} />
      </Island>,
    );

    const button = getByRole(document.body, "button");
    assert.strictEqual(button.textContent, "Count 10");

    hydrateIslands([TestComponent]);

    assert.strictEqual(button.textContent, "Count 10");
    await userEvent.click(button);
    assert.strictEqual(button.textContent, "Count 11");
  });
});
