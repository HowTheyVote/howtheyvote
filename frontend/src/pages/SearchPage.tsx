import { type VotesQueryResponse, searchVotes } from "../api";
import App from "../components/App";
import BaseLayout from "../components/BaseLayout";
import Hero from "../components/Hero";
import Pagination from "../components/Pagination";
import SearchForm from "../components/SearchForm";
import Stack from "../components/Stack";
import VoteCards from "../components/VoteCards";
import Wrapper from "../components/Wrapper";
import { firstQueryValue, redirect } from "../lib/http";
import { getLogger } from "../lib/logging";
import type { Loader, Page, Request } from "../lib/server";

const log = getLogger();

export const loader: Loader<VotesQueryResponse> = async (request: Request) => {
  const q = firstQueryValue(request.query, "q") || "";
  const page = Number.parseInt(
    firstQueryValue(request.query, "page") || "1",
    10,
  );

  const { data } = await searchVotes({ query: { q, page } });

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

  return data;
};

function pageUrl(query: string, page: number): string {
  const params = new URLSearchParams();

  if (query !== "") {
    params.set("q", query);
  }

  if (page > 1) {
    params.set("page", page.toString());
  }

  return `/votes?${params.toString()}`;
}

export const SearchPage: Page<VotesQueryResponse> = ({ data, request }) => {
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
            <Wrapper>
              <Stack space="lg">
                <VoteCards
                  groupByDate={!request.query.q}
                  votes={data.results}
                />

                <Pagination
                  next={data.has_next && pageUrl(query, data.page + 1)}
                  prev={data.has_prev && pageUrl(query, data.page - 1)}
                />
              </Stack>
            </Wrapper>
          </div>
        </Stack>
      </BaseLayout>
    </App>
  );
};
