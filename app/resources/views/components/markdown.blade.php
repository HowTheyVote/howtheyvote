<x-stack space="xs" {{ $attributes->bem('markdown') }}>
    {!! Str::markdown($slot) !!}
</x-stack>
