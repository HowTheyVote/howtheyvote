export default () => ({
  title: '',

  init() {
    this.title = this.$refs.title.textContent.toLowerCase().trim();
  },

  matchesSearchQuery() {
    const query = this.searchQuery.toLowerCase().trim();

    if (!query) {
      return true;
    }

    return (this.title + this.subtitle).includes(query);
  },
});
