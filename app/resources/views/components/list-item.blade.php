@props([
    'avatarUrl' => null,
    'avatarStyle' => null,
    'title' => null,
    'subtitle' => null,
    'position' => null,
    'stats' => null,
])

<li {{ $attributes->bem('list-item') }}>
    <x-avatar :url="$avatarUrl" class="list-item__avatar" :style="$avatarStyle" />

    <div class="list-item__text">
        <strong>{{ $title }}</strong>
        <br>
        {{ $subtitle }}

        @if ($stats)
            <x-vote-result-chart :stats="$stats" style="slim"/>
        @endif
    </div>

    @if ($position)
        <span class="visually-hidden">
            {{ Str::lower($position->label) }}
        </span>

        <x-thumb :position="$position" style="circle" class="list-item__thumb"/>
    @endif
</li>
