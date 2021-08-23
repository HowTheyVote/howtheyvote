const ENDPOINT = 'http://localhost:7700/indexes/voting_lists/search';
const LIMIT = 10;

export default () => ({
  query: '',
  results: [],
  totalResults: null,
  page: 0,

  init() {
    this.search();
  },

  formatDate(isoString) {
    const options = {
      weekday: 'short',
      day: 'numeric',
      month: 'long',
      year: 'numeric',
    };

    return new Date(isoString).toLocaleString('en-US', options);
  },

  async search() {
    // Reset page
    this.page = 0;

    const data = await this.getResults();
    this.results = data.hits;
    this.totalResults = data.nbHits;
  },

  async loadMore() {
    this.page += 1;
    const data = await this.getResults();
    this.results.push(...data.hits);
  },

  get hasMoreResults() {
    return this.results.length < this.totalResults;
  },

  async getResults() {
    const response = await fetch(this.searchUrl);
    return await response.json();
  },

  get searchUrl() {
    const params = new URLSearchParams({
      q: this.query,
      limit: LIMIT,
      offset: this.page * LIMIT,
    });

    return ENDPOINT + '?' + params;
  },
});
