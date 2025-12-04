const SORT_ORDERS = ["relevance", "newest", "oldest"] as const;
export type SortOrder = (typeof SORT_ORDERS)[0];
export const DEFAULT_SORT_ORDER: SortOrder = "relevance";

export const FILTERS = [
  "geo_areas",
  "responsible_committees",
  "date[lte]",
  "date[gte]",
] as const;

export const FACETS = ["geo_areas", "responsible_committees"] as const;

export const SORT_PARAMS = {
  relevance: {},
  newest: { sort_by: "date", sort_order: "desc" },
  oldest: { sort_by: "date", sort_order: "asc" },
} as const;

export class SearchQuery {
  base: string;
  q: string | undefined;
  filters: Record<string, string[]>;
  sort: (typeof SORT_ORDERS)[0];
  page: number;

  constructor(base: string) {
    this.base = base;
    this.filters = {};
    this.sort = DEFAULT_SORT_ORDER;
    this.page = 1;
  }

  static fromUrl(url: URL) {
    const params = url.searchParams;
    let instance = new SearchQuery(url.pathname);

    const q = params.get("q");

    if (q) {
      instance = instance.setQ(q);
    }

    for (const key of FILTERS) {
      if (params.has(key)) {
        for (const value of params.getAll(key)) {
          instance = instance.addFilter(key, value);
        }
      }
    }

    const sort = params.get("sort");

    if (sort) {
      instance = instance.setSort(sort);
    }

    const page = params.get("page");

    if (page) {
      instance = instance.setPage(parseInt(page, 10));
    }

    return instance;
  }

  toUrl() {
    const params = new URLSearchParams();

    if (this.q) {
      params.set("q", this.q);
    }

    for (const [key, values] of Object.entries(this.filters)) {
      for (const value of values) {
        params.append(key, value);
      }
    }

    if (this.sort && this.sort !== DEFAULT_SORT_ORDER) {
      params.append("sort", this.sort);
    }

    if (this.page && this.page > 1) {
      params.append("page", this.page.toString());
    }

    if (params.size === 0) {
      return this.base;
    }

    // Return string instead of `URL` object, because `URL` doesn’t support relative URLs.
    return `${this.base}?${params.toString()}`;
  }

  clone() {
    const instance = new SearchQuery(this.base);
    instance.q = this.q;
    instance.filters = structuredClone(this.filters);
    instance.sort = this.sort;
    instance.page = this.page;
    return instance;
  }

  setQ(q: string) {
    const clone = this.clone();
    clone.q = q;
    return clone;
  }

  addFilter(key: string, value: string) {
    const clone = this.clone();

    if (!clone.filters[key]) {
      clone.filters[key] = [];
    }

    clone.filters[key].push(value);

    return clone;
  }

  getFilter(key: string) {
    return this.filters[key] || [];
  }

  withoutFilter(key: string, value: string) {
    const clone = this.clone();
    clone.filters[key] = clone.filters[key].filter((other) => other !== value);
    return clone;
  }

  setSort(order: string) {
    const clone = this.clone();

    if (isSortOrder(order)) {
      clone.sort = order;
    }

    return clone;
  }

  setPage(page: number) {
    const clone = this.clone();
    clone.page = page;
    return clone;
  }
}

function isSortOrder(order: string): order is SortOrder {
  return (SORT_ORDERS as ReadonlyArray<string>).includes(order);
}
