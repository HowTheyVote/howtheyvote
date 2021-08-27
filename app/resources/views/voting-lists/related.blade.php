<x-app title="{{ $votingList->displayTitle }} · Related Votes">
    <x-base-layout>
        <x-stack space="lg">
            <x-voting-list.header
                :votingList="$votingList"
                :minimal="true"
            />

            <div class="padding--h">
                <x-wrapper>
                    <x-callout :heading="__('votes.related.callout-heading')" >
                        {!! __('votes.related.final-vote', ['url' => route('voting-list.show', $votingList)]) !!}
                    </x-callout>
                </x-wrapper>
            </div>

            <div class="padding--h">
                <x-wrapper>
                    <x-stack space="xs">
                        @foreach ($relatedVotes as $relatedVote)
                            <x-vote-card
                                :vote="$relatedVote"
                                :heading="$relatedVote->subtitle"
                                text=""
                            />
                        @endforeach
                    </x-stack>
                </x-wrapper>
            </div>
        </x-stack>
    </x-base-layout>
</x-app>
