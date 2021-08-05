@props([
    'avatarUrl' => null,
    'avatarStyle' => null,
    'title' => null,
    'emoji' => null,
    'subtitle' => null,
    'position' => null,
    'stats' => null,
])

<li
    {{ $attributes->bem('list-item') }}
    x-data="listItem"
    x-show="matchesSearchQuery"
>
    @if ($avatarUrl)
        <x-avatar
            :url="$avatarUrl"
            class="list-item__avatar"
            :style="$avatarStyle"
        />
    @endif

    <div class="list-item__text">
        <strong x-ref="title">
            {{ $title }} {{ $emoji }}
        </strong>

        <div class="list-item__subtitle" x-ref="subtitle">
            {{ $subtitle }}
        </div>

        @if ($stats)
            <x-vote-result-chart
                :stats="$stats"
                style="slim"
                class="list-item__chart"
            />
        @endif
    </div>

    @if ($position)
        <span class="visually-hidden">
            {{ Str::lower($position->label) }}
        </span>

        <x-thumb :position="$position" style="circle" class="list-item__thumb"/>
    @endif
</li>
