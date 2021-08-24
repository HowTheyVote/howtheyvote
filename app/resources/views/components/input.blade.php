@props(['type' => 'text', 'size' => null])

<input type="{{ $type }}" {{ $attributes->bem('input', $size) }} />
