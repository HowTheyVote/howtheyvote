<x-button
    size="lg"
    style="block"
    x-on:click="loadMore()"
    x-bind:disabled="loading"
    x-text="loading
        ? '{{ __('components.search.loading') }}'
        : '{{ __('components.search.load-more') }}'
    "
></x-button>
