@props([
    'text' => null,
    'heading' => null,
])

<div {{ $attributes->bem('action-panel') }}>
    <x-stack space="xxs">
        <h2 class="beta">{{ $heading }}</h2>
        <p>{{ $text }}</p>
    </x-stack>
    <div class="action-panel__action">
        {{ $slot }}
    </div>
</div>
