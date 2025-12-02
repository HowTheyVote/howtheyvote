import type { ComponentProps } from "preact";
import type { JSX } from "preact/jsx-runtime";
import type { FacetOption } from "../api";
import type { SearchQuery } from "../lib/search";
import Button from "./Button";
import Dialog from "./Dialog";
import SearchFacet from "./SearchFacet";
import SearchFacetDateOptions from "./SearchFacetDateOptions";
import SearchFacetMultiselectOptions from "./SearchFacetMultiselectOptions";

import "./SearchFiltersDialog.css";

type SearchFiltersDialogProps = Pick<
  ComponentProps<typeof Dialog>,
  "open" | "onOpenChange"
> & {
  searchQuery: SearchQuery;
  facets: Record<string, FacetOption[]>;
};

function SearchFiltersDialog({
  searchQuery,
  facets,
  open,
  onOpenChange,
}: SearchFiltersDialogProps) {
  // By default, when submitting a form, the URL query includes parameters for empty
  // fields. That’s a little ugly in case of our filters, so we handle the form
  // submission ourselves.
  const onSubmit = (event: JSX.TargetedSubmitEvent<HTMLFormElement>) => {
    event.preventDefault();
    const data = new FormData();

    for (const [key, value] of new FormData(event.currentTarget)) {
      if (value) {
        data.append(key, value);
      }
    }

    // @ts-expect-error: https://github.com/microsoft/TypeScript/issues/30584
    const params = new URLSearchParams(data);
    window.location.search = params.toString();
  };

  return (
    <Dialog
      title="Filter results"
      open={open}
      onOpenChange={onOpenChange}
      className="search-filters-dialog"
    >
      <form method="get" onSubmit={onSubmit}>
        <input name="q" type="hidden" value={searchQuery.q} />
        <input name="sort" type="hidden" value={searchQuery.sort} />
        <div class="search-filters-dialog__facets">
          <SearchFacet label="Date">
            <SearchFacetDateOptions
              field="date"
              start={searchQuery.getFilter("date[gte]")[0]}
              end={searchQuery.getFilter("date[lte]")[0]}
            />
          </SearchFacet>
          <SearchFacet label="Country">
            <SearchFacetMultiselectOptions
              field="geo_areas"
              options={facets.geo_areas}
              selected={searchQuery.getFilter("geo_areas")}
              searchLabel="Filter countries"
            />
          </SearchFacet>
          <SearchFacet label="Responsible committee">
            <SearchFacetMultiselectOptions
              field="responsible_committees"
              options={facets.responsible_committees}
              selected={searchQuery.getFilter("responsible_committees")}
              searchLabel="Filter committees"
            />
          </SearchFacet>
        </div>
        <div class="search-filters-dialog__submit">
          <Button type="submit">Apply filters</Button>
        </div>
      </form>
    </Dialog>
  );
}

export default SearchFiltersDialog;
