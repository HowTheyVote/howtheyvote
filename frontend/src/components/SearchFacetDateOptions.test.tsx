import { strict as assert } from "node:assert";
import { describe, it } from "node:test";
import { render, screen } from "@testing-library/preact";
import SearchFacetDateOptions from "./SearchFacetDateOptions";

describe("SearchFacetDateOptions", () => {
  it("renders date inputs for start and end date", () => {
    render(<SearchFacetDateOptions field="date" />);

    screen.getByLabelText("From");
    screen.getByLabelText("Until");
  });

  it("handles selected values", () => {
    render(
      <SearchFacetDateOptions
        field="date"
        start="2025-01-01"
        end="2025-12-31"
      />,
    );

    const from = screen.getByLabelText<HTMLInputElement>("From");
    const to = screen.getByLabelText<HTMLInputElement>("Until");

    assert.strictEqual(from.value, "2025-01-01");
    assert.strictEqual(to.value, "2025-12-31");
  });
});
