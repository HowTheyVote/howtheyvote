import type { SearchQuery } from "../lib/search";
import Select from "./Select";

type SortSelectProps = {
  searchQuery: SearchQuery;
};

export default function SortSelect({ searchQuery }: SortSelectProps) {
  // Always navigate to first page after changing sort order
  searchQuery = searchQuery.setPage(1);

  return (
    <Select
      value={searchQuery.sort}
      options={{
        relevance: "Relevance",
        newest: "Newest first",
        oldest: "Oldest first",
      }}
      onChange={(event) => {
        const url = searchQuery.setSort(event.currentTarget.value).toUrl();
        window.location.href = url;
      }}
    />
  );
}
