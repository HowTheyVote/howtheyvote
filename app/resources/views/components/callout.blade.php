@props([
    'heading' => null,
    'text' => null,
    'style' => null,
])

<div {{ $attributes->bem('callout', $style) }}>
    <x-stack space="xxs">
        <h2 class="callout__heading gamma">{{ $heading }}</h2>
        <p>{{ $slot }}</p>
    </x-stack>
</div>
