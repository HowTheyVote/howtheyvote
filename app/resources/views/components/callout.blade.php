@props([
    'heading' => null,
    'text' => null,
    'style' => null,
])

<div {{ $attributes->bem('callout', $style) }}>
    <x-stack space="xxs">
        @if ($heading)
            <h2 class="callout__heading gamma">{{ $heading }}</h2>
        @endif

        <p>{{ $slot }}</p>
    </x-stack>
</div>
