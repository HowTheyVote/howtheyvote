@props([
    'type' => 'text',
    'size' => null,
    'style' => null,
])

<input type="{{ $type }}" {{ $attributes->bem('input', [$size, $style]) }} />
