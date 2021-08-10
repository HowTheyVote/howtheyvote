export default searchKey => ({
  searchKey: searchKey && searchKey.toLowerCase(),

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
});
