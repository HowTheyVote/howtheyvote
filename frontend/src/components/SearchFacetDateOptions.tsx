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
        <div class="search-facet-date-options__input">
          <Input
            type="date"
            name={`${field}[gte]`}
            placeholder="From"
            value={start}
          />
        </div>
      </label>
      <label class="search-facet-date-options__date">
        <div class="search-facet-date-options__label">Until</div>
        <div class="search-facet-date-options__input">
          <Input
            type="date"
            name={`${field}[lte]`}
            placeholder="Until"
            value={end}
          />
        </div>
      </label>
    </div>
  );
}

export default SearchFacetDateOptions;
