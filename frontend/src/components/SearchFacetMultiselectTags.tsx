import type { FacetOption } from "../api";
import type { SearchQuery } from "../lib/search";
import Tag from "./Tag";

type SearchFacetMultiselectTagsProps = {
  searchQuery: SearchQuery;
  id: string;
  options: FacetOption[];
};

function SearchFacetMultiselectTags({
  searchQuery,
  id,
  options,
}: SearchFacetMultiselectTagsProps) {
  const selectedOptions = searchQuery
    .getFilter(id)
    .map((value) => {
      return options.find((option) => option.value === value);
    })
    .filter((option): option is FacetOption => !!option);

  return selectedOptions.map(({ value, label, short_label }) => (
    <li key={value}>
      <Tag
        deleteLink={searchQuery.withoutFilter(id, value).toUrl()}
        deleteLabel="Remove filter"
      >
        {short_label ? <abbr title={label}>{short_label}</abbr> : label}
      </Tag>
    </li>
  ));
}

export default SearchFacetMultiselectTags;
