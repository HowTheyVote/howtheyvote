import type { MemberVotesQueryResponse, VotesQueryResponse } from "../api";
import { Island } from "../lib/islands";
import { getSearchFeedbackFormUrl } from "../lib/links";
import { SearchQuery } from "../lib/search";
import Button from "./Button";
import Callout from "./Callout";
import EmptyState from "./EmptyState";
import Pagination from "./Pagination";
import SearchActions from "./SearchActions";
import Stack from "./Stack";
import Thumb from "./Thumb";
import VoteCard from "./VoteCard";
import VoteCards from "./VoteCards";

type SearchResultsProps = {
  url: URL;
} & (
  | { data: VotesQueryResponse; thumb?: never }
  | { data: MemberVotesQueryResponse; thumb?: "position" }
);

function SearchResults({ url, data, thumb }: SearchResultsProps) {
  const searchQuery = SearchQuery.fromUrl(url);

  return (
    <Stack space="lg">
      <Island>
        <SearchActions
          // Pass URL as string instead of SearchQuery object because all island props
          // need to be JSON serializable
          url={url.toString()}
          total={data.total}
          facets={data.facets}
        />
      </Island>

      {data.query && data.query !== searchQuery.q && (
        <Callout>
          Showing results for{" "}
          <a href={searchQuery.setQ(data.query).toUrl()}>
            <strong>{data.query}</strong>
          </a>
          {". "}There were no results for <strong>{searchQuery.q}</strong>.
        </Callout>
      )}

      {data.total <= 3 &&
        data.query === searchQuery.q &&
        data.corrected_query && (
          <Callout>
            Did you mean{" "}
            <a href={searchQuery.setQ(data.corrected_query).toUrl()}>
              <strong>{data.corrected_query}</strong>
            </a>
            ?
          </Callout>
        )}

      {data.total === 0 && (
        <SearchFeedback title="No results found." query={searchQuery.q} />
      )}

      {data.results.length > 0 && (
        <VoteCards
          groupByDate={!searchQuery.q && !searchQuery.hasFilters()}
          votes={data.results}
        >
          {({ vote }: { vote: (typeof data)["results"][number] }) => (
            <VoteCard
              key={vote.id}
              vote={vote}
              thumb={
                "position" in vote &&
                thumb === "position" && (
                  <Thumb style="circle" position={vote.position} />
                )
              }
            />
          )}
        </VoteCards>
      )}

      {(data.has_next || data.has_prev) && (
        <Pagination
          next={data.has_next && searchQuery.setNextPage().toUrl()}
          prev={data.has_prev && searchQuery.setPrevPage().toUrl()}
        />
      )}

      {data.total > 0 && (
        <SearchFeedback
          title="Not finding what you are looking for?"
          query={searchQuery.q}
        />
      )}
    </Stack>
  );
}

function SearchFeedback({ title, query }: { title: string; query?: string }) {
  return (
    <EmptyState
      action={
        <Button
          as="a"
          href={getSearchFeedbackFormUrl(query || "")}
          target="_blank"
          rel="noreferrer noopener"
        >
          Share feedback
        </Button>
      }
    >
      <strong>{title}</strong>
      <br />
      Let us know what you are searching for to help us improve search.
    </EmptyState>
  );
}

export default SearchResults;
