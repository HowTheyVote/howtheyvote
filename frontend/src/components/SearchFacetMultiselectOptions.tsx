import { useState } from "preact/hooks";
import type { FacetOption } from "../api";
import { normalize } from "../lib/normalization";
import Button from "./Button";
import Icon from "./Icon";
import Input from "./Input";

import "./SearchFacetMultiselectOptions.css";

type SearchFacetMultiselectOptionsProps = {
  field: string;
  options: FacetOption[];
  selected?: string[];
  searchLabel?: string;
};

const MAX_OPTIONS = 5;

function SearchFacetMultiselectOptions({
  field,
  options,
  selected = [],
  searchLabel = "Search options",
}: SearchFacetMultiselectOptionsProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [query, setQuery] = useState("");

  let filteredOptions = options.filter(
    ({ label, short_label }) =>
      normalize(label).includes(normalize(query)) ||
      (short_label && normalize(short_label).includes(normalize(query))),
  );

  const selectedOptions = filteredOptions.filter(({ value }) =>
    selected.includes(value),
  );
  const maxOptions = Math.max(MAX_OPTIONS, selectedOptions.length);

  // Show selected options at the beginning of the list
  filteredOptions = filteredOptions.sort(
    (a, b) =>
      Number(selected.includes(b.value)) - Number(selected.includes(a.value)),
  );

  return (
    <div class="search-facet-multiselect-options">
      {options.length > maxOptions && (
        <label>
          <span class="visually-hidden">{searchLabel}</span>
          <Input
            className="search-facet-multiselect-options__search"
            type="search"
            placeholder={searchLabel}
            value={query}
            onInput={(event) => setQuery(event.currentTarget.value)}
          />
        </label>
      )}

      {filteredOptions.map(({ value, label, short_label, count }, index) => (
        <label
          key={value}
          class="search-facet-multiselect-options__option"
          hidden={!isExpanded && index >= maxOptions ? true : undefined}
        >
          <input
            type="checkbox"
            name={`${field}`}
            value={value}
            checked={selected.includes(value) ? true : undefined}
          />
          <span class="search-facet-multiselect-options__label">
            {label} {short_label && `(${short_label})`}
          </span>{" "}
          <span class="search-facet-multiselect-options__count">
            <span aria-hidden="true">{count}</span>
            <span class="visually-hidden">{`(${count} results)`}</span>
          </span>
        </label>
      ))}

      {filteredOptions.length > maxOptions && (
        <Button
          className="search-facet-multiselect-options__toggle"
          size="sm"
          style="ghost"
          aria-expanded={isExpanded ? "true" : "false"}
          onClick={() => setIsExpanded(!isExpanded)}
        >
          {isExpanded
            ? "Show fewer"
            : `Show ${options.length - maxOptions} more`}
          <Icon name="chevron-down" />
        </Button>
      )}
    </div>
  );
}

export default SearchFacetMultiselectOptions;
