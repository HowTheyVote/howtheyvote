@props(['votingList'])

<x-action-panel
    :heading="__('voting-lists.download.heading')"
    :text="__('voting-lists.download.text')"
>
    <x-button
        size="lg"
        href="{{ route('voting-list.csv', $votingList) }}"
    >
        {{ __('voting-lists.download.button-label') }}
    </x-button>
</x-action-panel>
