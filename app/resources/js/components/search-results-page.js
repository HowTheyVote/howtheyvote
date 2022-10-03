const LIMIT = 10;
const ATTRIBUTES = [
  'id',
  'display_title',
  'date',
  'session_id',
  'session_display_title',
];
const HIGHLIGHT_ATTRIBUTES = ['display_title'];
const CROP_ATTRIBUTES = ['display_title'];
const CROP_LENGTH = 150;

export default (options = {}) => ({
  endpoint: options.endpoint,
  index: options.index,
  apiKey: options.apiKey,
  memberId: options.memberId,

  page: 0,
  results: [],
  totalNumberOfResults: null,

  loading: false,
  initialLoadCompleted: false,
  abortController: null,

  init() {
    this.restoreFromUrl();
    this.search();

    this.$watch('$store.searchQuery', () => this.search());
  },

  async search() {
    // Reset page
    this.page = 0;

    const data = await this.getResults();
    this.results = data.hits;
    this.totalNumberOfResults = data.estimatedTotalHits;

    this.persistToUrl();
  },

  async loadMore() {
    const currentNumberOfResults = this.numberOfResults;

    this.page += 1;
    const data = await this.getResults();
    this.results.push(...data.hits);

    this.persistToUrl();

    this.$nextTick(() => {
      this.focusResult(currentNumberOfResults + 1);
    });
  },

  reset() {
    this.$store.searchQuery = '';
    this.search();
  },

  get numberOfResults() {
    return this.results.length;
  },

  get resultsGroupedBySession() {
    const sessions = this.results
      // Sort by descending date...
      .sort((a, b) => b.date - a.date)

      // ... then group by session id
      .reduce((groups, result) => {
        groups[result.session_id] = groups[result.session_id] || {
          id: result.session_id,
          displayTitle: result.session_display_title,
          votes: [],
        };

        groups[result.session_id].votes.push(result);

        return groups;
      }, {});

    // Sort sessions by the date of first (i.e. the
    // most recent) vote, as the order might be mixed
    // up by grouping
    return Object.values(sessions).sort((a, b) => {
      return b.votes[0].date - a.votes[0].date;
    });
  },

  get hasMoreResults() {
    return this.numberOfResults < this.totalNumberOfResults;
  },

  get hasQuery() {
    return this.$store.searchQuery.length > 0;
  },

  async getResults() {
    // Cancel any pending requests
    if (this.abortController) {
      this.abortController.abort();
    }

    this.loading = true;
    this.abortController = new AbortController();

    let additionalAttributes = ['result'];
    let filters = [];

    if (this.memberId !== null) {
      additionalAttributes = [`votings.${this.memberId}`];
      filters = [`members = ${this.memberId}`];
    }

    const response = await fetch(this.searchUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Meili-API-Key': this.apiKey,
      },
      signal: this.abortController.signal,
      body: JSON.stringify({
        q: this.$store.searchQuery,
        filter: filters,
        limit: LIMIT,
        offset: this.page * LIMIT,
        attributesToRetrieve: [...ATTRIBUTES, ...additionalAttributes],
        attributesToHighlight: HIGHLIGHT_ATTRIBUTES,
        attributesToCrop: CROP_ATTRIBUTES,
        cropLength: CROP_LENGTH,
      }),
    });

    this.loading = false;
    this.initialLoadCompleted = true;

    return await response.json();
  },

  focusResult(n) {
    const results = this.$refs.results.querySelectorAll('a');
    const nthResult = results[n - 1];

    if (!nthResult) {
      return;
    }

    nthResult.focus();
  },

  persistToUrl() {
    const url = new URL(window.location.href);

    if (this.$store.searchQuery) {
      url.searchParams.set('q', this.$store.searchQuery);
    } else {
      url.searchParams.delete('q');
    }

    window.history.replaceState({}, '', url);
  },

  restoreFromUrl() {
    const url = new URL(window.location.href);
    const query = url.searchParams.get('q');

    if (query) {
      this.$store.searchQuery = query;
    }
  },

  get searchUrl() {
    const url = new URL(this.endpoint);
    url.pathname = `/indexes/${this.index}/search`;

    return url.toString();
  },

  formatDate(timestamp) {
    const options = {
      weekday: 'short',
      day: 'numeric',
      month: 'long',
      year: 'numeric',
    };

    return new Date(timestamp * 1000).toLocaleString('en-US', options);
  },
});
