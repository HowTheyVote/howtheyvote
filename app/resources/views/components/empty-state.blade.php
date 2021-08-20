@props([ 'title' => null ])

<x-stack space="xs" {{ $attributes->bem('empty-state') }}>
    <h2 class="beta">{{ $title }}</h2>
    {{ $slot }}
</x-stack>
