import { strict as assert } from "node:assert";
import { describe, it } from "node:test";
import { render, screen } from "@testing-library/preact";
import { SearchQuery } from "../lib/search";
import SearchFacetDateTag from "./SearchFacetDateTag";

describe("SearchFacetDateTag", () => {
  it("ignores invalid dates", () => {
    const query = SearchQuery.fromUrl(
      new URL("https://howtheyvote.eu/votes?date[gte]=invalid"),
    );

    const { container } = render(
      <SearchFacetDateTag id="date[gte]" searchQuery={query} prefix="From" />,
    );

    assert.strictEqual(container.innerHTML, "");
  });

  it("renders prefix and formatted date", () => {
    const query = SearchQuery.fromUrl(
      new URL("https://howtheyvote.eu/votes?date[gte]=2025-01-01"),
    );

    render(
      <SearchFacetDateTag id="date[gte]" searchQuery={query} prefix="From" />,
    );

    screen.getByText("From Jan 1, 2025");
  });

  it("has link to remove filter", () => {
    const query = SearchQuery.fromUrl(
      new URL(
        "https://howtheyvote.eu/votes?date[gte]=2025-01-01&date[lte]=2025-12-31",
      ),
    );

    render(
      <SearchFacetDateTag id="date[gte]" searchQuery={query} prefix="From" />,
    );

    const link = screen.getByRole<HTMLAnchorElement>("link", {
      name: "Remove filter",
    });
    assert.strictEqual(
      decodeURIComponent(link.href),
      "/votes?date[lte]=2025-12-31",
    );
  });
});
