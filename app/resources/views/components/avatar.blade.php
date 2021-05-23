@props(['url' => null])

<div {{ $attributes->bem('avatar') }}>
    <img src="{{ $url }}" alt="" loading="lazy" />
</div>
