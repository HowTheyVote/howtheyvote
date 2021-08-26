<x-button
    size="lg"
    style="block"
    x-on:click="loadMore()"
    x-bind:disabled="loading"
    x-text="loading
        ? '{{ __('components.search-results-page.loading') }}'
        : '{{ __('components.search-results-page.load-more') }}'
    "
></x-button>
