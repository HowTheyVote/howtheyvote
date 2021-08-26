@props(['votingList'])

<x-callout style="warning" :heading="__('voting-lists.non-final-callout.heading')">
    @if ($votingList->vote->isAmendmentVote())
        {{
            __('voting-lists.non-final-callout.amendment', [
                'amendment' => lcfirst($votingList->vote->subtitle),
            ])
        }}
    @endif

    @if ($votingList->vote->isSeparateVote())
        {{
            __('voting-lists.non-final-callout.separate', [
                'separate' => lcfirst($votingList->vote->subtitle),
            ])
        }}
    @endif

    @if ($votingList->vote->finalVote?->url)
    {!!
        __('voting-lists.non-final-callout.text', [
            'url' => $votingList->vote->finalVote->url,
        ])
    !!}
    @endif
</x-callout>
