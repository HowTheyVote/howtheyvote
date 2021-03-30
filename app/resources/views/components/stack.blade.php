@props(['space' => null])

<div {{ $attributes->bem('stack', $space) }}>
    {{ $slot }}
</div>
