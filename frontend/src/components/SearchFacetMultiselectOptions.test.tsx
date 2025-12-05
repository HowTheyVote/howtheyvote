import { strict as assert } from "node:assert";
import { describe, it } from "node:test";
import { render, screen } from "@testing-library/preact";
import userEvent from "@testing-library/user-event";
import SearchFacetMultiselectOptions from "./SearchFacetMultiselectOptions";

describe("SearchFacetMultiselectOptions", () => {
  it("renders options as checkboxes", () => {
    render(
      <SearchFacetMultiselectOptions
        field="foo"
        options={[
          { value: "1", label: "Option 1", count: 1 },
          { value: "2", label: "Option 2", count: 2 },
          { value: "3", label: "Option 3", count: 3 },
        ]}
      />,
    );

    assert.strictEqual(screen.getAllByRole("checkbox").length, 3);
    screen.getByRole("checkbox", { name: "Option 1 (1 results)" });
    screen.getByRole("checkbox", { name: "Option 2 (2 results)" });
    screen.getByRole("checkbox", { name: "Option 3 (3 results)" });
  });

  it("shows only the first few options by default", async () => {
    const options = [...Array(100).keys()].map((i) => ({
      value: (i + 1).toString(),
      label: `Option ${i + 1}`,
      count: i + 1,
    }));

    const { rerender } = render(
      <SearchFacetMultiselectOptions
        field="foo"
        options={options.slice(0, 3)}
      />,
    );

    assert.strictEqual(screen.getAllByRole("checkbox").length, 3);
    assert.strictEqual(screen.queryByRole("button"), null);

    rerender(<SearchFacetMultiselectOptions field="foo" options={options} />);

    assert.strictEqual(screen.getAllByRole("checkbox").length, 5);

    const show = screen.getByRole("button", { name: "Show 95 more" });
    await userEvent.click(show);

    assert.strictEqual(screen.getAllByRole("checkbox").length, 100);

    const hide = screen.getByRole("button", { name: "Show fewer" });
    await userEvent.click(hide);

    assert.strictEqual(screen.getAllByRole("checkbox").length, 5);
  });

  it("always shows selected values at the top", async () => {
    const options = [...Array(100).keys()].map((i) => ({
      value: (i + 1).toString(),
      label: `Option ${i + 1}`,
      count: i + 1,
    }));

    // Select every 10th option
    const selected = [...Array(10).keys()].map((i) =>
      ((i + 1) * 10).toString(),
    );

    render(
      <SearchFacetMultiselectOptions
        field="foo"
        options={options}
        selected={selected}
      />,
    );

    let inputs = screen.getAllByRole<HTMLInputElement>("checkbox");
    assert.strictEqual(inputs.length, 10);
    assert.deepEqual(
      inputs.map((input) => input.value),
      ["10", "20", "30", "40", "50", "60", "70", "80", "90", "100"],
    );

    const show = screen.getByRole("button", { name: "Show 90 more" });
    await userEvent.click(show);

    inputs = screen.getAllByRole<HTMLInputElement>("checkbox");
    assert.strictEqual(inputs.length, 100);
    assert.strictEqual(inputs[0].value, "10");
    assert.strictEqual(inputs[9].value, "100");
    assert.strictEqual(inputs[10].value, "1");
    assert.strictEqual(inputs[11].value, "2");
    assert.strictEqual(inputs[99].value, "99");
  });

  it("handles selected values", () => {
    render(
      <SearchFacetMultiselectOptions
        field="foo"
        options={[
          { value: "1", label: "Option 1", count: 1 },
          { value: "2", label: "Option 2", count: 2 },
          { value: "3", label: "Option 3", count: 3 },
        ]}
        selected={["2"]}
      />,
    );

    assert.strictEqual(
      screen.getAllByRole("checkbox", { checked: false }).length,
      2,
    );
    assert.strictEqual(
      screen.getAllByRole("checkbox", { checked: true }).length,
      1,
    );
    screen.getByRole("checkbox", {
      name: "Option 2 (2 results)",
      checked: true,
    });
  });

  it("keeps selection state after hiding options", async () => {
    const options = [...Array(100).keys()].map((i) => ({
      value: (i + 1).toString(),
      label: `Option ${i + 1}`,
      count: i + 1,
    }));

    render(<SearchFacetMultiselectOptions field="foo" options={options} />);

    await userEvent.click(screen.getByRole("button", { name: "Show 95 more" }));
    const checkbox = screen.getByRole("checkbox", {
      name: /Option 50/,
      checked: false,
    });
    await userEvent.click(checkbox);
    screen.getByRole("checkbox", { name: /Option 50/, checked: true });

    await userEvent.click(screen.getByRole("button", { name: "Show fewer" }));
    await userEvent.click(screen.getByRole("button", { name: "Show 95 more" }));
    screen.getByRole("checkbox", { name: /Option 50/, checked: true });
  });

  it("has search input if there are many options", async () => {
    const { rerender } = render(
      <SearchFacetMultiselectOptions
        field="foo"
        options={[
          {
            value: "CONT",
            label: "Budgetary Control",
            short_label: "CONT",
            count: 1,
          },
          {
            value: "ENVI",
            label: "Environment, Climate and Food Safety",
            short_label: "ENVI",
            count: 2,
          },
          {
            value: "LIBE",
            label: "Civil Liberties, Justice and Home Affairs",
            short_label: "LIBE",
            count: 3,
          },
        ]}
      />,
    );

    assert.strictEqual(screen.queryByRole("searchbox"), null);

    rerender(
      <SearchFacetMultiselectOptions
        field="foo"
        options={[
          {
            value: "CONT",
            label: "Budgetary Control",
            short_label: "CONT",
            count: 1,
          },
          {
            value: "ENVI",
            label: "Environment, Climate and Food Safety",
            short_label: "ENVI",
            count: 2,
          },
          {
            value: "LIBE",
            label: "Civil Liberties, Justice and Home Affairs",
            short_label: "LIBE",
            count: 3,
          },
          {
            value: "ECON",
            label: "Economic and Monetary Affairs",
            short_label: "ECON",
            count: 4,
          },
          {
            value: "AFET",
            label: "Foreign Affairs",
            short_label: "AFET",
            count: 5,
          },
          { value: "BUDG", label: "Budgets", short_label: "BUDG", count: 6 },
        ]}
      />,
    );

    const search = screen.getByRole("searchbox", { name: "Search options" });

    await userEvent.type(search, "budget");
    assert.strictEqual(screen.getAllByRole("checkbox").length, 2);
    screen.getByRole("checkbox", { name: "Budgets (BUDG) (6 results)" });
    screen.getByRole("checkbox", {
      name: "Budgetary Control (CONT) (1 results)",
    });

    await userEvent.clear(search);
    await userEvent.type(search, "afet");
    assert.strictEqual(screen.getAllByRole("checkbox").length, 2);
    screen.getByRole("checkbox", {
      name: "Foreign Affairs (AFET) (5 results)",
    });
    screen.getByRole("checkbox", {
      name: "Environment, Climate and Food Safety (ENVI) (2 results)",
    });
  });
});
