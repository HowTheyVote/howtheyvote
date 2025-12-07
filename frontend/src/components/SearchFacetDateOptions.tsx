import { useState } from "preact/hooks";
import { CURRENT_TERM_START_DATE } from "../config";
import { toISODateString } from "../lib/dates";
import Input from "./Input";
import Tag from "./Tag";

import "./SearchFacetDateOptions.css";

type SearchFacetDateOptions = {
  field: string;
  start?: string;
  end?: string;
};

function SearchFacetDateOptions({ field, start, end }: SearchFacetDateOptions) {
  const [startValue, setStartValue] = useState(start || "");
  const [endValue, setEndValue] = useState(end || "");

  const setRange = (startValue: string | null, endValue: string | null) => {
    setStartValue(startValue || "");
    setEndValue(endValue || "");
  };

  const today = new Date();
  const startOfYear = toISODateString(new Date(today.getFullYear(), 0, 1));
  const thirtyDaysAgo = toISODateString(
    new Date(today.getFullYear(), today.getMonth(), today.getDate() - 30),
  );

  return (
    <div class="search-facet-date-options">
      <label class="search-facet-date-options__date">
        <div class="search-facet-date-options__label">From</div>
        <div class="search-facet-date-options__input">
          <Input
            type="date"
            name={`${field}[gte]`}
            placeholder="From"
            value={startValue}
            onInput={(event) => setStartValue(event.currentTarget.value)}
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
            value={endValue}
            onInput={(event) => setEndValue(event.currentTarget.value)}
          />
        </div>
      </label>
      <div class="search-facet-date-options__quick-select">
        <Tag
          as="button"
          type="button"
          onClick={() => setRange(CURRENT_TERM_START_DATE, null)}
        >
          Current term
        </Tag>
        <Tag
          as="button"
          type="button"
          onClick={() => setRange(startOfYear, null)}
        >
          This year
        </Tag>
        <Tag
          as="button"
          type="button"
          onClick={() => setRange(thirtyDaysAgo, null)}
        >
          Last 30 days
        </Tag>
      </div>
    </div>
  );
}

export default SearchFacetDateOptions;
