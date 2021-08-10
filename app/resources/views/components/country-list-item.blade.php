@props([
    'country' => null,
    'stats' => null,
])

<x-list-item
    :title="$country->label"
    :emoji="$country->emoji"
    :subtitle="__('voting-lists.groups.count', [
        'voted' => $stats['voted'],
        'total' => $stats['active'],
    ])"
    :stats="$stats"
    :search-key="$country->label"
    {{ $attributes }}
/>
