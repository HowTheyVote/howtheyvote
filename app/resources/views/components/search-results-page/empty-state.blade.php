<x-empty-state :title="__('components.search-results-page.empty-state.title')">
    <p>
        {{ __('components.search-results-page.empty-state.text') }}
        <a
            href="?query="
            x-on:click.prevent="reset()"
        >{{ __('components.search-results-page.empty-state.action') }}</a>.
    </p>
</x-empty-state>
