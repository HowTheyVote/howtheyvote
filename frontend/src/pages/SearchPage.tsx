import { getVotes, type VotesQueryResponse } from "../api";
import App from "../components/App";
import BaseLayout from "../components/BaseLayout";
import Hero from "../components/Hero";
import Pagination from "../components/Pagination";
import SearchActions from "../components/SearchActions";
import SearchForm from "../components/SearchForm";
import Stack from "../components/Stack";
import VoteCards from "../components/VoteCards";
import Wrapper from "../components/Wrapper";
import { PUBLIC_URL } from "../config";
import { redirect } from "../lib/http";
import { Island } from "../lib/islands";
import { getLogger } from "../lib/logging";
import { SearchQuery } from "../lib/search";
import type { Loader, Page, Request } from "../lib/server";

const log = getLogger();

const SORT_PARAMS = {
  relevance: {},
  newest: { sort_by: "date", sort_order: "desc" },
  oldest: { sort_by: "date", sort_order: "asc" },
} as const;

type SearchPageData = VotesQueryResponse & {
  searchQuery: SearchQuery;
};

export const loader: Loader<SearchPageData> = async (request: Request) => {
  const searchQuery = SearchQuery.fromUrl(new URL(request.url, PUBLIC_URL));

  const { data } = await getVotes({
    query: {
      q: searchQuery.q,
      page: searchQuery.page,
      facets: ["geo_areas", "responsible_committees"],
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
  const { searchQuery } = data;

  return (
    <App title={"All Votes"}>
      <BaseLayout>
        <Stack space="lg">
          <Hero
            title="All Votes"
            text="Explore recent votes or search our database by subject."
            action={<SearchForm style="elevated" value={searchQuery.q} />}
          />
          <div class="px">
            <Wrapper className="search-page">
              <Stack space="lg">
                <Island>
                  <SearchActions
                    // Pass URL as string because all island props need to be JSON serializable
                    url={url.toString()}
                    total={data.total}
                    facets={data.facets}
                  />
                </Island>

                <VoteCards
                  groupByDate={
                    !searchQuery.q &&
                    Object.keys(searchQuery.filters).length === 0
                  }
                  votes={data.results}
                />

                <Pagination
                  next={
                    data.has_next &&
                    searchQuery.setPage(searchQuery.page + 1).toUrl()
                  }
                  prev={
                    data.has_prev &&
                    searchQuery.setPage(searchQuery.page - 1).toUrl()
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
