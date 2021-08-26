@props(['votingList'])

<x-action-panel
    :heading="__('voting-lists.related-votes-list.heading')"
    :text="__('voting-lists.related-votes-list.text')"
>
    <x-button
        size="lg"
        href="{{ route('voting-list.related', $votingList) }}"
    >
        {{ __('voting-lists.related-votes-list.button-label') }}
    </x-button>
</x-action-panel>
