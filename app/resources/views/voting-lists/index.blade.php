<x-app title="Votes">
    <x-base-layout>
        <x-stack>
            <h1 class="alpha">All Votes</h1>
            <x-search-input />
            <x-search-results-page
                :endpoint="config('scout.meilisearch.public_endpoint')"
                :apiKey="config('scout.meilisearch.public_key')"
                index="voting_lists"
            />
        </x-stack>
    </x-base-layout>
</x-app>
