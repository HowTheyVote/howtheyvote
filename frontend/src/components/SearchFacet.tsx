import type { ComponentChildren } from "preact";

import "./SearchFacet.css";

type SearchFacetProps = {
  label: string;
  children: ComponentChildren;
};

function SearchFacet({ label, children }: SearchFacetProps) {
  return (
    <fieldset class="search-facet">
      <legend class="search-facet__label">{label}</legend>
      {children}
    </fieldset>
  );
}

export default SearchFacet;
