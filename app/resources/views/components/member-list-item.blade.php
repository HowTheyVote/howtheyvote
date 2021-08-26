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
    :url="$url"
    search-key="{{ $member->full_name }} {{ $member->country->label }}"
    {{ $attributes }}
/>
