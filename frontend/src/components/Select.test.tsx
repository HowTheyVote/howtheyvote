import { strict as assert } from "node:assert";
import { describe, it } from "node:test";
import { render, screen } from "@testing-library/preact";
import Select from "./Select";

describe("Select", () => {
  it("renders options", () => {
    render(<Select options={{ foo: "Foo", bar: "Bar" }} />);
    const options = screen.getAllByRole<HTMLOptionElement>("option");

    assert.strictEqual(options[0].value, "foo");
    assert.strictEqual(options[0].textContent, "Foo");
    assert.strictEqual(options[1].value, "bar");
    assert.strictEqual(options[1].textContent, "Bar");

    // First option is selected by default
    screen.getByRole("option", { selected: true, name: "Foo" });
  });

  it("selects option based on value prop", () => {
    render(<Select options={{ foo: "Foo", bar: "Bar" }} value="bar" />);
    screen.getByRole("option", { selected: true, name: "Bar" });
  });
});
