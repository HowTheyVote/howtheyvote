import { searchVotes, type VotesQueryResponseWithFacets } from "../api";
import App from "../components/App";
import BaseLayout from "../components/BaseLayout";
import Hero from "../components/Hero";
import Pagination from "../components/Pagination";
import SearchActions from "../components/SearchActions";
import SearchForm from "../components/SearchForm";
import Stack from "../components/Stack";
import VoteCards from "../components/VoteCards";
import Wrapper from "../components/Wrapper";
import { allQueryValues, firstQueryValue, redirect } from "../lib/http";
import { Island } from "../lib/islands";
import { getLogger } from "../lib/logging";
import type { Loader, Page, Request } from "../lib/server";
import { oneOf } from "../lib/validation";

const log = getLogger();

const SORT_PARAMS = {
  relevance: {},
  newest: { sort_by: "date", sort_order: "desc" },
  oldest: { sort_by: "date", sort_order: "asc" },
} as const;

const FILTER_FIELDS = [
  "geo_areas",
  "responsible_committees",
  "date[gte]",
  "date[lte]",
] as const;

type SortOptions = "relevance" | "newest" | "oldest";

type SearchPageData = VotesQueryResponseWithFacets & {
  query: string;
  sort: SortOptions;
  filters: Record<string, string[]>;
};

export const loader: Loader<SearchPageData> = async (request: Request) => {
  const q = firstQueryValue(request.query, "q") || "";

  const page = Number.parseInt(
    firstQueryValue(request.query, "page") || "1",
    10,
  );

  const sort = oneOf(
    firstQueryValue(request.query, "sort") || "",
    ["relevance", "newest", "oldest"] as const,
    "relevance",
  );

  const filters = Object.fromEntries(
    FILTER_FIELDS.map((field) => [
      field,
      allQueryValues(request.query, field),
    ]).filter(([_, values]) => values.length > 0),
  );

  const { data } = await searchVotes({
    query: {
      q,
      page,
      facets: ["geo_areas", "responsible_committees"],
      ...filters,
      ...SORT_PARAMS[sort],
    },
  });

  if (!request.isBot && q) {
    log.info({
      msg: "Handling search request",
      // Apply some basic normalization to make log aggregation easier
      query: q.toLowerCase().replace(/\s+/, " "),
    });
  }

  if (
    data.results.length === 1 &&
    data.results[0].reference === request.query.q
  ) {
    redirect(`/votes/${data.results[0].id}`);
  }

  return { ...data, query: q, sort, filters };
};

function pageUrl(data: SearchPageData, page: number): string {
  const params = new URLSearchParams();

  if (data.query !== "") {
    params.set("q", data.query);
  }

  for (const [field, values] of Object.entries(data.filters)) {
    for (const value of values) {
      params.append(field, value);
    }
  }

  params.set("sort", data.sort);

  if (page > 1) {
    params.set("page", page.toString());
  }

  return `/votes?${params.toString()}`;
}

export const SearchPage: Page<SearchPageData> = ({ data }) => {
  return (
    <App title={"All Votes"}>
      <BaseLayout>
        <Stack space="lg">
          <Hero
            title="All Votes"
            text="Explore recent votes or search our database by subject."
            action={<SearchForm style="elevated" value={data.query} />}
          />
          <div class="px">
            <Wrapper className="search-page">
              <Stack space="lg">
                <Island>
                  <SearchActions
                    total={data.total}
                    query={data.query}
                    facets={data.facets}
                    filters={data.filters}
                    sort={data.sort}
                  />
                </Island>

                <VoteCards
                  groupByDate={
                    !data.query && Object.keys(data.filters).length === 0
                  }
                  votes={data.results}
                />

                <Pagination
                  next={data.has_next && pageUrl(data, data.page + 1)}
                  prev={data.has_prev && pageUrl(data, data.page - 1)}
                />
              </Stack>
            </Wrapper>
          </div>
        </Stack>
      </BaseLayout>
    </App>
  );
};
