@props([
    'member' => null,
    'position' => null,
])

<x-list-item
    avatar-url="https://www.europarl.europa.eu/mepphoto/{{ $member->web_id }}.jpg"
    :title="$member->full_name"
    :subtitle="$member->group->abbreviation.' · '.$member->country->label"
    :position="$position"
    {{ $attributes }}
/>
