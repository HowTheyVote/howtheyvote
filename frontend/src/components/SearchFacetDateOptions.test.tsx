import { strict as assert } from "node:assert";
import { after, before, describe, it, mock } from "node:test";
import { render, screen } from "@testing-library/preact";
import userEvent from "@testing-library/user-event";
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

  describe("Quick filter buttons", () => {
    before(() => {
      mock.timers.enable({
        apis: ["Date"],
        now: new Date("2025-12-01"),
      });
    });

    after(() => mock.timers.reset());

    it("clicking buttons sets date inputs to predefined range", async () => {
      render(
        <SearchFacetDateOptions
          field="date"
          start="2025-02-15"
          end="2025-07-31"
        />,
      );

      const from = screen.getByLabelText<HTMLInputElement>("From");
      const to = screen.getByLabelText<HTMLInputElement>("Until");

      const buttons = screen.getAllByRole("button");
      assert.strictEqual(buttons.length, 3);

      const currentTerm = screen.getByRole("button", { name: "Current term" });
      const thisYear = screen.getByRole("button", { name: "This year" });
      const lastThirtyDays = screen.getByRole("button", {
        name: "Last 30 days",
      });

      assert.strictEqual(from.value, "2025-02-15");
      assert.strictEqual(to.value, "2025-07-31");

      await userEvent.click(currentTerm);
      assert.strictEqual(from.value, "2024-07-16");
      assert.strictEqual(to.value, "");

      await userEvent.click(thisYear);
      assert.strictEqual(from.value, "2025-01-01");
      assert.strictEqual(to.value, "");

      await userEvent.click(lastThirtyDays);
      assert.strictEqual(from.value, "2025-11-01");
      assert.strictEqual(to.value, "");
    });
  });
});
