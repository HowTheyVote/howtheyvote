@props(['parse' => true])

<div space="xs" {{ $attributes->bem('markdown') }}>
    {!! $parse ? Str::markdown($slot) : $slot !!}
</div>
