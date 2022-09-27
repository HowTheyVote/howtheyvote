<x-app title="{{ __('voting-lists.title') }}">
    <x-base-layout>
        <x-stack space="lg">
            <x-hero>
                <x-slot:title>
                    {{ __('voting-lists.title') }}
                </x-slot>

                <x-slot:text>
                    {{ __('voting-lists.subtitle') }}
                </x-slot>

                <x-slot:action>
                    <x-search-input />
                </x-slot>
            </x-hero>

            <div class="padding--h">
                <x-wrapper>
                    <x-search-results-page
                        :endpoint="config('scout.meilisearch.public_endpoint')"
                        :apiKey="config('scout.meilisearch.public_key')"
                        index="voting_lists"
                    />
                </x-wrapper>
            </div>
        </x-stack>
    </x-base-layout>
</x-app>
