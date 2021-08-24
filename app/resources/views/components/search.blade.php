@props([
    'endpoint' => null,
    'index' => null,
    'apiKey' => null,
])

<div
    {{ $attributes->bem('search') }}
    x-data="search({{ json_encode([
        'endpoint' => $endpoint,
        'index' => $index,
        'apiKey' => $apiKey,
    ]) }})"
>
    <x-stack>
        <x-stack space="xs">
            <x-input
                type="search"
                :placeholder="__('components.search.placeholder')"
                x-model="query"
                x-on:input="search()"
            />

            <template x-if="query && totalNumberOfResults > 0">
                <p aria-live="polite">
                    <span x-text="numberOfResults"></span>/<span x-text="totalNumberOfResults"></span>
                    {{ __('components.search.results') }}
                </p>
            </template>
        </x-stack>

        <div x-ref="results">
            <template x-if="!hasQuery">
                <x-stack space="lg">
                    <template
                        x-for="session in resultsGroupedBySession"
                        v-bind:key="session.id"
                    >
                        <x-stack space="sm">
                            <h2 class="beta" x-text="session.displayTitle"></h2>
                            <template x-for="vote in session.votes" v-bind:key="vote.id">
                                <x-search-result />
                            </template>
                        </x-stack>
                    </template>
                </x-stack>
            </template>

            <template x-if="hasQuery">
                <x-stack space="sm">
                    <template x-for="vote in results" v-bind:key="vote.id">
                        <x-search-result />
                    </template>
                </x-stack>
            </template>
        </div>

        <template x-if="hasMoreResults">
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
        </template>

        <template x-if="hasQuery && totalNumberOfResults <= 0">
            <x-empty-state :title="__('components.search.empty-state.title')">
                <p>
                    {{ __('components.search.empty-state.text') }}
                    <a
                        href="?query="
                        x-on:click.prevent="reset()"
                    >{{ __('components.search.empty-state.action') }}</a>.
                </p>
            </x-empty-state>
        </template>

        <noscript>
            <x-empty-state :title="__('components.search.noscript.title')">
                <p>{{ __('components.search.noscript.text') }}</p>
            </x-empty-state>
        </noscript>
    </x-stack>
</div>
