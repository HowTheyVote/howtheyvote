@props([
    'size' => null,
    'href' => null,
    'style' => null,
    'tag' => null,
])

@if ($href)
    <a {{ $attributes->bem('button', [$size, $style]) }} href="{{ $href }}">
        {{ $slot }}
    </a>
@elseif ($tag)
    <{{ $tag }} {{ $attributes->bem('button', [$size, $style]) }}>
        {{ $slot }}
    </{{ $tag }}>
@else
    <button {{ $attributes->bem('button', [$size, $style]) }}>
        {{ $slot }}
    </button>
@endif
