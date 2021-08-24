<x-empty-state :title="__('components.search.empty-state.title')">
    <p>
        {{ __('components.search.empty-state.text') }}
        <a
            href="?query="
            x-on:click.prevent="reset()"
        >{{ __('components.search.empty-state.action') }}</a>.
    </p>
</x-empty-state>
