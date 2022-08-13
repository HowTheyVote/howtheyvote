@props([
    'truncate' => false,
    'showMore' => __('components.list.show-more'),
    'showLess' => __('components.list.show-less'),
    'searchable' => false,
    'searchPlaceholder' => __('components.list.search-placeholder'),
    'actions' => null,
])

@php
    $initialState = [
        'truncate' => $truncate,
        'searchQuery' => '',
    ];
@endphp

<div
    {{ $attributes->bem('list') }}
    x-data="{{ json_encode($initialState) }}"
    x-bind:class="(truncate && searchQuery === '') ? 'list--truncated' : ''"
>
    <div class="list__action-bar" x-cloak>
        @if ($searchable)
            <x-input class="list__search"
                type="search"
                x-model="searchQuery"
                :placeholder="$searchPlaceholder"
            />
        @endif

        @if ($actions)
            {{ $actions }}
        @endif
    </div>

    <ul>
        {{ $slot }}
    </ul>

    @if ($truncate)
        <x-button
            size="lg"
            class="list__toggle"
            x-on:click="truncate = !truncate"
            x-bind:aria-expanded="truncate ? 'false' : 'true'"
            x-show="searchQuery === ''"
            x-cloak
        >
            <span x-show="truncate">{{ $showMore }}</span>
            <span x-show="!truncate">{{ $showLess }}</span>
        </x-button>
    @endif
</div>
