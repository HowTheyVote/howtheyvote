@props([
    'endpoint' => null,
    'index' => null,
])

<div x-data="search('{{ $endpoint }}', '{{ $index }}')">
    <x-stack space="xs">
        <x-input
            type="search"
            :placeholder="__('components.search.placeholder')"
            x-model="query"
            x-on:input="search()"
        />

        <p>
            <span x-text="totalResults"></span>
            {{ __('components.search.results') }}
        </p>
    </x-stack>

    <x-stack>
        <template x-for="vote in results" :key="vote.id">
            <article class="vote-card">
                <a :href="`/votes/${vote.id}`">
                    <x-thumb
                        class="vote-card__thumb"
                        result="adopted"
                        style="circle"
                        x-show="vote.result === 'ADOPTED'"
                    />

                    <x-thumb
                        class="vote-card__thumb"
                        result="rejected"
                        style="circle"
                        x-show="vote.result === 'REJECTED'"
                    />

                    <div>
                        <strong x-text="vote.display_title"></strong>
                        <p x-text="formatDate(vote.date)"></p>
                    </div>
                </a>
            </article>
        </template>

        <template x-if="hasMoreResults">
            <x-button
                x-on:click="loadMore()"
                size="lg"
                style="block"
            >
                {{ __('components.search.load-more') }}
            </x-button>
        </template>
    </x-stack>
</div>
