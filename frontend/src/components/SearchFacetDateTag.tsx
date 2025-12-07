import { formatDate, isValidDate } from "../lib/dates";
import type { SearchQuery } from "../lib/search";
import Tag from "./Tag";

type SearchFacetDateTagProps = {
  searchQuery: SearchQuery;
  id: string;
  prefix: string;
};

function SearchFacetDateTag({
  searchQuery,
  id,
  prefix,
}: SearchFacetDateTagProps) {
  const value = searchQuery.getFilter(id)?.[0];
  const date = new Date(value);

  if (!isValidDate(date)) {
    return null;
  }

  return (
    <li>
      <Tag
        deleteLink={searchQuery.withoutFilter(id, value).toUrl()}
        deleteLabel="Remove filter"
      >
        {prefix} {formatDate(date)}
      </Tag>
    </li>
  );
}

export default SearchFacetDateTag;
