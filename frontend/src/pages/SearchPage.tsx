import * as Sentry from "@sentry/node";
import { getVotes, type VotesQueryResponse } from "../api";
import App from "../components/App";
import BaseLayout from "../components/BaseLayout";
import Hero from "../components/Hero";
import SearchForm from "../components/SearchForm";
import SearchResults from "../components/SearchResults";
import Stack from "../components/Stack";
import Wrapper from "../components/Wrapper";
import { PUBLIC_URL } from "../config";
import { redirect } from "../lib/http";
import { getLogger } from "../lib/logging";
import { FACETS, SearchQuery, SORT_PARAMS } from "../lib/search";
import type { Loader, Page, Request } from "../lib/server";

const log = getLogger();

type SearchPageData = VotesQueryResponse & {
  searchQuery: SearchQuery;
};

function normalizeQuery(query?: string) {
  return query?.toLowerCase().trim().replaceAll(/\s+/g, " ");
}

export const loader: Loader<SearchPageData> = async (request: Request) => {
  const searchQuery = SearchQuery.fromUrl(new URL(request.url, PUBLIC_URL));

  // Apply some basic normalization to make log aggregation easier
  const rawQuery = searchQuery?.q;
  const normalizedQuery = normalizeQuery(rawQuery);

  if (!request.isBot && normalizedQuery) {
    log.info({
      msg: "Handling search request",
      normalizedQuery,
      rawQuery,
    });

    Sentry.metrics.count("searches", 1, {
      attributes: {
        normalizedQuery,
        rawQuery,
      },
    });
  }

  let { data } = await getVotes({
    query: {
      q: searchQuery.q,
      page: searchQuery.page,
      // The array spread is a workaround to make the readonly array a mutable array
      // See https://github.com/hey-api/openapi-ts/issues/1641
      facets: [...FACETS],
      ...searchQuery.filters,
      ...SORT_PARAMS[searchQuery.sort],
    },
  });

  if (!request.isBot && data.results.length === 0) {
    log.info({
      msg: "Search without results",
      normalizedQuery,
      rawQuery,
    });

    Sentry.metrics.count("searches_no_results", 1, {
      attributes: {
        normalizedQuery,
        rawQuery,
      },
    });
  }

  if (!request.isBot && data.corrected_query) {
    const rawCorrectedQuery = data.corrected_query;
    const normalizedCorrectedQuery = normalizeQuery(rawCorrectedQuery);

    log.info({
      msg: "Search with corrected spelling",
      normalizedQuery,
      rawQuery,
      normalizedCorrectedQuery,
      rawCorrectedQuery,
    });

    Sentry.metrics.count("searches_corrected_spelling", 1, {
      attributes: {
        normalizedQuery,
        rawQuery,
        normalizedCorrectedQuery,
        rawCorrectedQuery,
      },
    });
  }

  // If the original query resulted in 0 results and there is a spelling correction,
  // repeat the search with the corrected spelling.
  if (data.total === 0 && data.corrected_query) {
    const { data: correctedData } = await getVotes({
      query: {
        q: data.corrected_query,
        page: searchQuery.page,
        // The array spread is a workaround to make the readonly array a mutable array
        // See https://github.com/hey-api/openapi-ts/issues/1641
        facets: [...FACETS],
        ...searchQuery.filters,
        ...SORT_PARAMS[searchQuery.sort],
      },
    });
    data = correctedData;
  }

  // This is a shortcut for power users. If a user searches for a resolution/report reference,
  // and there is only a single (main) vote for that reference, we redirect to that vote.
  if (
    data.results.length === 1 &&
    data.results[0].reference === searchQuery.q
  ) {
    redirect(`/votes/${data.results[0].id}`);
  }

  return { ...data, searchQuery };
};

export const SearchPage: Page<SearchPageData> = ({ data, request }) => {
  const url = new URL(request.url, PUBLIC_URL);
  const searchQuery = SearchQuery.fromUrl(url);

  return (
    <App title={"All Votes"}>
      <BaseLayout>
        <Stack space="lg">
          <Hero
            title="All Votes"
            text="Explore recent votes or search our database by subject."
            action={
              <SearchForm
                action={searchQuery.base}
                size="lg"
                style="elevated"
                value={searchQuery.q}
              />
            }
          />
          <div class="px">
            <Wrapper>
              <SearchResults url={url} data={data} />
            </Wrapper>
          </div>
        </Stack>
      </BaseLayout>
    </App>
  );
};
