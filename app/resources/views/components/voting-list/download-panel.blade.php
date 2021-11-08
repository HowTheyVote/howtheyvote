@props(['votingList'])

<x-action-panel
    :heading="__('voting-lists.download.heading')"
    :text="__('voting-lists.download.text')"
>
    <x-button
        size="lg"
        href="{{ route('voting-list.csv', $votingList) }}"
    >
        {{ __('voting-lists.download.button-label-csv') }}
    </x-button>

    <x-button
        size="lg"
        href="{{ route('voting-list.json', $votingList) }}"
    >
        {{ __('voting-lists.download.button-label-json') }}
    </x-button>


</x-action-panel>
