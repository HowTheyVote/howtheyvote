import { strict as assert } from "node:assert";
import { describe, it } from "node:test";
import { render, screen } from "@testing-library/preact";
import Button from "./Button";

describe("Button", () => {
  it("can render as a button", () => {
    render(<Button>Click me!</Button>);
    const button = screen.getByRole("button", { name: "Click me!" });
    assert.strictEqual(button.getAttribute("type"), "button");
  });

  it("can render as a link", () => {
    render(
      <Button as="a" href="https://example.org">
        Link
      </Button>,
    );
    const link = screen.getByRole("link", { name: "Link" });
    assert.strictEqual(link.getAttribute("href"), "https://example.org");
  });
});
