@props([
    'size' => null,
    'href' => null,
])

@if ($href)
    <a {{ $attributes->bem('button', $size) }} href="{{ $href }}">
        {{ $slot }}
    </a>
@else
    <button {{ $attributes->bem('button', $size) }}>
        {{ $slot }}
    </button>
@endif
