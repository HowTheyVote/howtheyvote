@props([
    'member' => null,
    'position' => null,
    'url' => null,
])

<x-list-item
    :avatar-url="$member->thumbnail_url"
    :title="$member->full_name"
    :subtitle="$member->group->abbreviation.' · '.$member->country->label"
    :position="$position"
    :url="route('members.show', ['member' => $member])"
    search-key="{{ $member->full_name }} {{ $member->country->label }}"
    :filter-key="$position->label"
    {{ $attributes }}
/>
