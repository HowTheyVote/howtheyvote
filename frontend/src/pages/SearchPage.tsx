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

export const loader: Loader<SearchPageData> = async (request: Request) => {
  const searchQuery = SearchQuery.fromUrl(new URL(request.url, PUBLIC_URL));

  const { data } = await getVotes({
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

  if (!request.isBot && searchQuery.q) {
    log.info({
      msg: "Handling search request",
      // Apply some basic normalization to make log aggregation easier
      query: searchQuery.q.toLowerCase().replace(/\s+/, " "),
    });
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
