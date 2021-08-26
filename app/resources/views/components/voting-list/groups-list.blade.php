@props(['groups'])

<x-list>
    @foreach ($groups as $group)
        <x-group-list-item :group="$group" :stats="$group->stats" />
    @endforeach
</x-list>
