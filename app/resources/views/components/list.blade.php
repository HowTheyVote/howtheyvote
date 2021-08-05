@props([
    'truncate' => false,
    'showMore' => 'Show more',
    'showLess' => 'Show less',
])

<div
    {{ $attributes->bem('list') }}
    @if ($truncate) x-data="{truncate: true}" @endif
    x-bind:class="truncate ? 'list--truncated' : ''"
>
    <ul>
        {{ $slot }}
    </ul>

    @if ($truncate)
        <x-button
            size="lg"
            class="list__toggle"
            x-on:click="truncate = !truncate"
            x-bind:aria-expanded="truncate ? 'false' : 'true'"
        >
            <span x-show="truncate">{{ $showMore }}</span>
            <span x-show="!truncate">{{ $showLess }}</span>
        </x-button>
    @endif
</div>
