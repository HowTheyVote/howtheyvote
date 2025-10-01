import { searchVotes, type VotesQueryResponse } from "../api";
import App from "../components/App";
import BaseLayout from "../components/BaseLayout";
import Hero from "../components/Hero";
import Pagination from "../components/Pagination";
import SearchForm from "../components/SearchForm";
import SortSelect from "../components/SortSelect";
import Stack from "../components/Stack";
import VoteCards from "../components/VoteCards";
import Wrapper from "../components/Wrapper";
import { firstQueryValue, redirect } from "../lib/http";
import { Island } from "../lib/islands";
import { getLogger } from "../lib/logging";
import type { Loader, Page, Request } from "../lib/server";
import { oneOf } from "../lib/validation";

import "./SearchPage.css";

const log = getLogger();

const SORT_PARAMS = {
  relevance: {},
  newest: { sort_by: "date", sort_order: "desc" },
  oldest: { sort_by: "date", sort_order: "asc" },
} as const;

type VotesSearchSortOptions = "relevance" | "newest" | "oldest";

type SearchPageData = VotesQueryResponse & {
  sort: VotesSearchSortOptions;
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

  const { data } = await searchVotes({
    query: {
      q,
      page,
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

  return { ...data, sort };
};

function pageUrl(
  query: string,
  sort: VotesSearchSortOptions,
  page: number,
): string {
  const params = new URLSearchParams();

  if (query !== "") {
    params.set("q", query);
  }

  params.set("sort", sort);

  if (page > 1) {
    params.set("page", page.toString());
  }

  return `/votes?${params.toString()}`;
}

export const SearchPage: Page<SearchPageData> = ({ data, request }) => {
  const query = firstQueryValue(request.query, "q") || "";

  return (
    <App title={"All Votes"}>
      <BaseLayout>
        <Stack space="lg">
          <Hero
            title="All Votes"
            text="Explore recent votes or search our database by subject."
            action={<SearchForm style="elevated" value={query} />}
          />
          <div class="px">
            <Wrapper className="search-page">
              <Stack space="lg">
                <div class="search-page__info">
                  <div>{data.total} results</div>
                  <label class="search-page__sort">
                    Sort by:
                    <Island>
                      <SortSelect value={data.sort} />
                    </Island>
                  </label>
                </div>

                <VoteCards
                  groupByDate={!request.query.q}
                  votes={data.results}
                />

                <Pagination
                  next={
                    data.has_next && pageUrl(query, data.sort, data.page + 1)
                  }
                  prev={
                    data.has_prev && pageUrl(query, data.sort, data.page - 1)
                  }
                />
              </Stack>
            </Wrapper>
          </div>
        </Stack>
      </BaseLayout>
    </App>
  );
};
