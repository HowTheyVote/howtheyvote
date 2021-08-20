const LIMIT = 10;
const ATTRIBUTES = ['id', 'display_title', 'date', 'result'];
const HIGHLIGHTS = ['display_title'];

export default (endpoint, index) => ({
  endpoint,
  index,

  query: '',
  page: 0,

  results: [],
  totalResults: null,

  abortController: null,

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
    // Cancel any pending requests
    if (this.abortController) {
      this.abortController.abort();
    }

    this.abortController = new AbortController();

    const response = await fetch(this.searchUrl, {
      signal: this.abortController.signal,
    });

    return await response.json();
  },

  get searchUrl() {
    const url = new URL(this.endpoint);

    url.pathname = `/indexes/${this.index}/search`;

    url.searchParams.set('q', this.query);
    url.searchParams.set('limit', LIMIT);
    url.searchParams.set('offset', this.page * LIMIT);
    url.searchParams.set('attributesToRetrieve', ATTRIBUTES.join(','));
    url.searchParams.set('attributesToHighlight', HIGHLIGHTS.join(','));

    return url.toString();
  },
});
