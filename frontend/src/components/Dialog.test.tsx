import { strict as assert } from "node:assert";
import { before, describe, it } from "node:test";
import { render, screen, within } from "@testing-library/preact";
import userEvent from "@testing-library/user-event";
import { useState } from "preact/hooks";
import Dialog from "./Dialog";

before(() => {
  // Need to mock `showModal`/`close` methods because jsdom currently doesn’t
  // have support for them: https://github.com/jsdom/jsdom/issues/3294
  window.HTMLDialogElement.prototype.showModal = function () {
    this.open = true;
  };

  window.HTMLDialogElement.prototype.close = function () {
    this.open = false;
  };
});

function Test() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      <button type="button" onClick={() => setIsOpen(!isOpen)}>
        Toggle
      </button>
      <Dialog title="Hello World" open={isOpen} onOpenChange={setIsOpen}>
        <p>Lorem ipsum dolor sit amet, consectetuer adipiscing elit.</p>
      </Dialog>
    </>
  );
}

describe("Dialog", () => {
  it("can be opened and closed", async () => {
    render(<Test />);
    assert.strictEqual(screen.queryByRole("dialog"), null);
    await userEvent.click(screen.getByRole("button", { name: "Toggle" }));
    const dialog = screen.getByRole("dialog", { name: "Hello World" });
    const close = within(dialog).getByRole("button", { name: "Close" });
    await userEvent.click(close);
    assert.strictEqual(screen.queryByRole("dialog"), null);
  });
});
