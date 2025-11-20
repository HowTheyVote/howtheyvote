import { useState } from "preact/hooks";
import type { FacetOption } from "../api";
import { SearchQuery } from "../lib/search";
import Button from "./Button";
import Icon from "./Icon";
import SearchFiltersDialog from "./SearchFiltersDialog";
import SortSelect from "./SortSelect";

import "./SearchActions.css";

type SearchActionsProps = {
  url: string;
  total: number;
  facets: Record<string, FacetOption[]>;
};

function SearchActions({ url, total, facets }: SearchActionsProps) {
  const [isFiltersDialogOpen, setIsFiltersDialogOpen] = useState(false);
  const searchQuery = SearchQuery.fromUrl(new URL(url));

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
          facets={facets}
          searchQuery={searchQuery}
        />
      </div>
      <label class="search-actions__sort">
        {"Sort by: "}
        <SortSelect searchQuery={searchQuery} />
      </label>
    </div>
  );
}

export default SearchActions;
