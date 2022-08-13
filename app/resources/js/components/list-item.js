export default ([searchKey, filterKey]) => ({
  searchKey: searchKey && searchKey.toLowerCase(),
  filterKey: filterKey && filterKey.toLowerCase(),

  matches() {
    return this.matchesSearchQuery() && this.matchesFilter();
  },

  matchesSearchQuery() {
    const query = this.searchQuery && this.searchQuery.toLowerCase().trim();

    if (!query) {
      return true;
    }

    if (!this.searchKey) {
      return false;
    }

    return this.searchKey.includes(query);
  },

  matchesFilter() {
    const filter = this.filter && this.filter.toLowerCase().trim();

    if (!filter) {
      return true;
    }

    if (!this.filterKey) {
      return false;
    }

    return this.filterKey === filter;
  },
});
