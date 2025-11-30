import { strict as assert } from "node:assert";
import { describe, it } from "node:test";
import { render, screen, within } from "@testing-library/preact";
import type { FacetOption } from "../api";
import { SearchQuery } from "../lib/search";
import SearchFacetMultiselectTags from "./SearchFacetMultiselectTags";

describe("SearchFacetMultiselectTags", () => {
  const options: FacetOption[] = [
    { value: "RUS", label: "Russia", count: 12 },
    { value: "UKR", label: "Ukraine", count: 10 },
    { value: "MDA", label: "Moldova", count: 8 },
  ];

  it("renders tag for every active filter option", () => {
    const query = SearchQuery.fromUrl(
      new URL("https://howtheyvote.eu/votes?geo_areas=UKR&geo_areas=RUS"),
    );

    render(
      <SearchFacetMultiselectTags
        id="geo_areas"
        searchQuery={query}
        options={options}
      />,
    );

    const items = screen.getAllByRole("listitem");

    within(items[0]).getByText("Ukraine");
    const removeUkraine = within(items[0]).getByRole<HTMLAnchorElement>(
      "link",
      { name: "Remove filter" },
    );
    assert.strictEqual(removeUkraine.href, "/votes?geo_areas=RUS");

    within(items[1]).getByText("Russia");
    const removeRussia = within(items[1]).getByRole<HTMLAnchorElement>("link", {
      name: "Remove filter",
    });
    assert.strictEqual(removeRussia.href, "/votes?geo_areas=UKR");
  });

  it("keeps the order of filter options from the URL", () => {
    const query1 = SearchQuery.fromUrl(
      new URL("https://howtheyvote.eu/votes?geo_areas=UKR&geo_areas=RUS"),
    );
    const query2 = SearchQuery.fromUrl(
      new URL("https://howtheyvote.eu/votes?geo_areas=RUS&geo_areas=UKR"),
    );

    const { rerender } = render(
      <SearchFacetMultiselectTags
        id="geo_areas"
        searchQuery={query1}
        options={options}
      />,
    );

    let tags = screen.getAllByRole("listitem");
    within(tags[0]).getByText("Ukraine");
    within(tags[1]).getByText("Russia");

    rerender(
      <SearchFacetMultiselectTags
        id="geo_areas"
        searchQuery={query2}
        options={options}
      />,
    );

    tags = screen.getAllByRole("listitem");
    within(tags[0]).getByText("Russia");
    within(tags[1]).getByText("Ukraine");
  });
});
