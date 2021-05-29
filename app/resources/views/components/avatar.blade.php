@props([
    'url' => null,
    'style' => null,
])

<div {{ $attributes->bem('avatar', $style) }}>
    <img src="{{ $url }}" alt="" loading="lazy" />
</div>
