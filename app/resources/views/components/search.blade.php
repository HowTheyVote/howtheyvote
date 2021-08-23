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

            <template x-if="query && totalResults > 0">
                <p>
                    <span x-text="totalResults"></span>
                    {{ __('components.search.results') }}
                </p>
            </template>
        </x-stack>

        <template x-if="!hasQuery">
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
        </template>

        <template x-if="hasQuery">
            <x-stack space="sm">
                <template x-for="vote in results" v-bind:key="vote.id">
                    <x-search-result />
                </template>
            </x-stack>
        </template>

        <template x-if="hasQuery && totalResults <= 0">
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

        <template x-if="hasMoreResults">
            <x-button x-on:click="loadMore()" size="lg" style="block">
                {{ __('components.search.load-more') }}
            </x-button>
        </template>
    </x-stack>
</div>
