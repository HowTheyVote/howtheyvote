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

  it("shows notice if corrected search query has been applied", () => {
    const url = new URL("https://howtheyvote.eu/votes?q=mercosour");

    const data = {
      query: "mercosur", // "mercosur" without "ou"
      corrected_query: undefined,
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

    screen.getByText(/Showing results for/);
    screen.getByRole("link", { name: "mercosur" });
    screen.getByText(/There were no results for/);
    screen.getByText(/mercosur/);
  });

  it("asks for feedback if there are no results", () => {
    const url = new URL("https://howtheyvote.eu/votes?q=chat+control");

    const data = {
      query: "chat control",
      corrected_query: undefined,
      total: 0,
      page: 1,
      page_size: 20,
      has_prev: false,
      has_next: false,
      results: [],
      facets: {},
    };

    render(<SearchResults url={url} data={data} />);

    screen.getByText(/No results found/);
    screen.getByRole("link", { name: "Share feedback" });
  });
});
