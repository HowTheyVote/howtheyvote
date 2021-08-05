@props([
    'group' => null,
    'stats' => null,
])

<x-list-item
    :title="$group->name"
    :subtitle="__('voting-lists.groups.count', [
        'voted' => $group->stats['voted'],
        'total' => $group->stats['active'],
    ])"
    :stats="$stats"
    avatarStyle="squared"
    avatarUrl="/assets/groups/{{ Str::lower($group->code) }}.svg"
    {{ $attributes }}
/>
