<x-app title="{{ $votingList->displayTitle }} · Related Votes">
    <x-base-layout>
        <x-stack>
            <h1 class="alpha">{{ $votingList->display_title }}</h1>

            <x-callout :heading="__('votes.related.callout-heading')" >
                {!! __('votes.related.primary-vote', ['url' => route('voting-list.show', $votingList)]) !!}
            </x-callout>

            <x-stack space="xs">
                @foreach ($relatedVotes as $relatedVote)
                    <x-vote-card
                        :vote="$relatedVote"
                        :heading="$relatedVote->subtitle"
                        text=""
                    />
                @endforeach
            </x-stack>
        </x-stack>
    </x-base-layout>
</x-app>
