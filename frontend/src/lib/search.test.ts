import { strict as assert } from "node:assert";
import { describe, it } from "node:test";
import { SearchQuery } from "./search";

describe("SearchQuery", () => {
  it("can be created from a URL", () => {
    const url = new URL(
      "https://howtheyvote.eu/votes?q=foo&geo_areas=DEU&geo_areas=FRA&responsible_committees=IMCO&sort=oldest&page=2",
    );
    const searchQuery = SearchQuery.fromUrl(url);

    assert.strictEqual(searchQuery.base, "/votes");
    assert.strictEqual(searchQuery.q, "foo");
    assert.deepStrictEqual(searchQuery.filters, {
      geo_areas: ["DEU", "FRA"],
      responsible_committees: ["IMCO"],
    });
    assert.deepStrictEqual(searchQuery.sort, "oldest");
    assert.deepStrictEqual(searchQuery.page, 2);
  });

  it("can be converted to URL", () => {
    const searchQuery = new SearchQuery("/votes");

    assert.strictEqual(searchQuery.toUrl(), "/votes");
    assert.strictEqual(searchQuery.setQ("foo").toUrl(), "/votes?q=foo");
    assert.strictEqual(
      searchQuery.addFilter("geo_areas", "DEU").toUrl(),
      "/votes?geo_areas=DEU",
    );
    assert.strictEqual(searchQuery.setPage(2).toUrl(), "/votes?page=2");
    assert.strictEqual(searchQuery.setPage(1).toUrl(), "/votes");
    assert.strictEqual(
      searchQuery.setSort("oldest").toUrl(),
      "/votes?sort=oldest",
    );
    assert.strictEqual(searchQuery.setSort("relevance").toUrl(), "/votes");
  });

  it("can be cloned", () => {
    const original = new SearchQuery("/votes").addFilter("geo_areas", "DEU");
    const clone = original.clone().addFilter("geo_areas", "FRA");

    assert.deepStrictEqual(original.filters.geo_areas, ["DEU"]);
    assert.deepStrictEqual(clone.filters.geo_areas, ["DEU", "FRA"]);
  });

  it("can set the query string", () => {
    const searchQuery = new SearchQuery("/votes").setQ("foo");
    assert.strictEqual(searchQuery.q, "foo");
  });

  it("can add filters", () => {
    let searchQuery = new SearchQuery("/votes");

    searchQuery = searchQuery.addFilter("geo_areas", "DEU");
    assert.deepStrictEqual(searchQuery.filters, {
      geo_areas: ["DEU"],
    });

    searchQuery = searchQuery.addFilter("geo_areas", "FRA");
    assert.deepStrictEqual(searchQuery.filters, {
      geo_areas: ["DEU", "FRA"],
    });
  });

  it("can get filter values", () => {
    const searchQuery = new SearchQuery("/votes").addFilter("geo_areas", "DEU");
    assert.deepStrictEqual(searchQuery.getFilter("geo_areas"), ["DEU"]);
    assert.deepStrictEqual(searchQuery.getFilter("responsible_committees"), []);
  });

  it("can set the page", () => {
    const searchQuery = new SearchQuery("/votes").setPage(2);
    assert.strictEqual(searchQuery.page, 2);
  });

  it("can set sort order", () => {
    const searchQuery = new SearchQuery("/votes").setSort("oldest");
    assert.strictEqual(searchQuery.sort, "oldest");
  });
});
