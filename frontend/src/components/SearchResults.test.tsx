import { describe, it } from "node:test";
import { render, screen } from "@testing-library/preact";
import SearchResults from "./SearchResults";

describe("SearchResults", () => {
  it("shows link to corrected search query", () => {
    const url = new URL("https://howtheyvote.eu/votes?q=defense");

    const data = {
      query: "defense",
      corrected_query: "defence",
      total: 1,
      page: 1,
      page_size: 20,
      has_prev: false,
      has_next: false,
      results: [
        {
          id: 1,
          timestamp: "2026-01-01T00:00:00+00:00",
          display_title: "Vote one",
          is_main: true,
          topics: [],
          geo_areas: [],
          eurovoc_concepts: [],
          oeil_subjects: [],
        },
      ],
      facets: {},
    };

    render(<SearchResults url={url} data={data} />);

    screen.getByText(/Did you mean/);
    screen.getByRole("link", { name: "defence" });
  });
});
