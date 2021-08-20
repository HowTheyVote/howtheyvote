<x-app title="Votes">
    <x-base-layout>
        <x-stack>
            <h1 class="alpha">Votes</h1>
            <x-search
                :endpoint="config('scout.meilisearch.public_endpoint')"
                :apiKey="config('scout.meilisearch.public_key')"
                index="voting_lists"
            />
        </x-stack>
    </x-base-layout>
</x-app>
