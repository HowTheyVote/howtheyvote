<x-app
    title="{{ $member->full_name }} · Votes Casted"
>
    <x-base-layout>
        <x-stack space="lg">
            <x-member.header :member="$member" :group="$group" />

            <section class="padding--h">
                <x-wrapper>
                    <x-search-results-page
                        :endpoint="config('scout.meilisearch.public_endpoint')"
                        :apiKey="config('scout.meilisearch.public_key')"
                        :memberId="$member->id"
                        index="voting_lists"
                    />
                </x-wrapper>
            </section>
        </x-stack>
    </x-base-layout>
</x-app>
