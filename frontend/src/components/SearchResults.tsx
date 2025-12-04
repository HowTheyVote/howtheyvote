import type { VotesQueryResponse } from "../api";
import { Island } from "../lib/islands";
import { SearchQuery } from "../lib/search";
import Pagination from "./Pagination";
import SearchActions from "./SearchActions";
import Stack from "./Stack";
import VoteCard from "./VoteCard";
import VoteCards from "./VoteCards";

type SearchResultsProps = {
  url: URL;
  data: VotesQueryResponse;
};

function SearchResults({ url, data }: SearchResultsProps) {
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

      <VoteCards
        groupByDate={!searchQuery.q && !searchQuery.hasFilters()}
        votes={data.results}
      >
        {({ vote }: { vote: (typeof data)["results"][number] }) => (
          <VoteCard key={vote.id} vote={vote} />
        )}
      </VoteCards>

      <Pagination
        next={data.has_next && searchQuery.setNextPage().toUrl()}
        prev={data.has_prev && searchQuery.setPrevPage().toUrl()}
      />
    </Stack>
  );
}

export default SearchResults;
