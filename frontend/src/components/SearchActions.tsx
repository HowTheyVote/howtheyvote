import { useState } from "preact/hooks";
import type { FacetOption } from "../api";
import Button from "./Button";
import SearchFiltersDialog from "./SearchFiltersDialog";
import SortSelect from "./SortSelect";

import "./SearchActions.css";
import Icon from "./Icon";

type SearchActionsProps = {
  total: number;
  query: string;
  facets: Record<string, FacetOption[]>;
  filters: Record<string, string[]>;
  sort: string;
};

function SearchActions({
  total,
  query,
  facets,
  filters,
  sort,
}: SearchActionsProps) {
  const [isFiltersDialogOpen, setIsFiltersDialogOpen] = useState(false);

  return (
    <div class="search-actions">
      <div class="search-actions__total">{total} results</div>
      <div class="search-actions__filters">
        <Button
          style="ghost"
          size="sm"
          onClick={() => setIsFiltersDialogOpen(true)}
        >
          Filters
          <Icon name="chevron-down" />
        </Button>
        <SearchFiltersDialog
          open={isFiltersDialogOpen}
          onOpenChange={setIsFiltersDialogOpen}
          query={query}
          sort={sort}
          facets={facets}
          filters={filters}
        />
      </div>
      <label class="search-actions__sort">
        {"Sort by: "}
        <SortSelect value={sort} />
      </label>
    </div>
  );
}

export default SearchActions;
