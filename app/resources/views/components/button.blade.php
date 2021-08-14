@props([
    'size' => null,
    'href' => null,
    'style' => null,
])

@if ($href)
    <a {{ $attributes->bem('button', $size) }} href="{{ $href }}">
        {{ $slot }}
    </a>
@else
    <button {{ $attributes->bem('button', [$size, $style]) }}>
        {{ $slot }}
    </button>
@endif
