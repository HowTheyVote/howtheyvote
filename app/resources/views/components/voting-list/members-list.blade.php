@props(['members'])

<x-list
    :truncate="true"
    :show-more="__('voting-lists.members.show-more')"
    :searchable="true"
    :search-placeholder="__('voting-lists.members.search-placeholder')"
>
    <x-slot name="actions">
        <x-position-select
            name="test"
            x-model="filter"
        />
    </x-slot>

    @foreach ($members as $member)
        <x-member-list-item
            :member="$member"
            :position="$member->pivot->position"
        />
    @endforeach
</x-list>
