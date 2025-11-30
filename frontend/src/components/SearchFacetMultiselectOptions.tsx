import { useState } from "preact/hooks";
import type { FacetOption } from "../api";
import Button from "./Button";
import Icon from "./Icon";

import "./SearchFacetMultiselectOptions.css";

type SearchFacetMultiselectOptionsProps = {
  field: string;
  options: FacetOption[];
  selected?: string[];
};

const MAX_OPTIONS = 5;

function SearchFacetMultiselectOptions({
  field,
  options,
  selected = [],
}: SearchFacetMultiselectOptionsProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  const selectedOptions = options.filter(({ value }) =>
    selected.includes(value),
  );
  const maxOptions = Math.max(MAX_OPTIONS, selectedOptions.length);

  // Show selected options at the beginning of the list
  options = options.sort(
    (a, b) =>
      Number(selected.includes(b.value)) - Number(selected.includes(a.value)),
  );

  return (
    <div class="search-facet-multiselect-options">
      {options.map(({ value, label, short_label, count }, index) => (
        <label
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

      {options.length > maxOptions && (
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
