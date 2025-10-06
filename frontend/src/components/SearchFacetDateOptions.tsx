import Input from "./Input";

import "./SearchFacetDateOptions.css";

type SearchFacetDateOptions = {
  field: string;
  start?: string;
  end?: string;
};

function SearchFacetDateOptions({ field, start, end }: SearchFacetDateOptions) {
  return (
    <div class="search-facet-date-options">
      <label class="search-facet-date-options__date">
        <div class="search-facet-date-options__label">From</div>
        <Input
          type="date"
          name={`${field}[gte]`}
          placeholder="From"
          value={start}
        />
      </label>
      <label class="search-facet-date-options__date">
        <div class="search-facet-date-options__label">To</div>
        <Input
          type="date"
          name={`${field}[lte]`}
          placeholder="To"
          value={end}
        />
      </label>
    </div>
  );
}

export default SearchFacetDateOptions;
