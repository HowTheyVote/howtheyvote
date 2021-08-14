@props([
    'title'=>null,
    'text'=>null,
    'url'=>null,
])

<x-button {{ $attributes->bem('share-button') }}
    x-data="{
        isVisible: 'share' in navigator,
        title: '{{ $title }}',
        text: '{{ $text }}',
        url: '{{ $url }}'
    }"
    x-on:click="navigator.share({title, text, url})"
    x-show="isVisible"
    x-cloak
>
Share this vote!
</x-button>
