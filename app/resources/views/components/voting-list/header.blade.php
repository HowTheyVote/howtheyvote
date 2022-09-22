@props([
    'votingList',
    'minimal' => false,
])

<div class="voting-list-header">
    <x-wrapper>
        <x-stack space="xs">
            <h1 class="alpha">{{ $votingList->display_title }}</h1>
            <p>
                <strong>
                    {{ $votingList->date->formatLocalized('%b %e, %Y') }}

                    @if ($votingList->vote)
                        ·
                        {{ $votingList->result->label() }}
                        <x-thumb style="circle" :result="$votingList->result" />
                    @endif
                </strong>
            </p>

            @if (! $minimal && $votingList->vote && $votingList->vote->isFInalVote() && $votingList->vote->summary)
                <p>
                    {{ $votingList->vote->summary->excerpt }}
                    <a href="{{ route('voting-list.summary', [
                        'votingList' => $votingList,
                    ]) }}">
                        {{ __('voting-lists.summary.read-more') }}
                    </a>
                </p>
            @endif
        </x-stack>

        @if (! $minimal && $votingList->vote && $votingList->vote->isFinalVote())
            <x-share-button
                class="voting-list-header__share"
                :title="$votingList->display_title"
                :text="$votingList->display_title"
                :url="route('voting-list.show', ['votingList' => $votingList])"
                style="block"
                size="lg"
            />
        @endif
    </x-wrapper>
</div>
