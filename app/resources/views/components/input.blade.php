@props(['type' => 'text'])

<input type="{{ $type }}" {{ $attributes->bem('input') }} />
