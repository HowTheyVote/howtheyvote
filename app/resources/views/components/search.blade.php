@props([
    'endpoint' => null,
    'index' => null,
    'apiKey' => null,
])

@once
    @push('head')
        <link rel="preconnect" href="{{ $endpoint }}" />
    @endpush
@endonce

<div
    {{ $attributes->bem('search') }}
    x-data="search({{ json_encode([
        'endpoint' => $endpoint,
        'index' => $index,
        'apiKey' => $apiKey,
    ]) }})"
>
    <x-stack>
        <x-stack space="xs">
            <x-search.input />

            <template x-if="query && totalNumberOfResults > 0">
                <x-search.results-count />
            </template>
        </x-stack>

        <x-search.results />

        <template x-if="hasMoreResults">
            <x-search.load-more-button />
        </template>

        <div aria-live="polite">
            <template x-if="hasQuery && totalNumberOfResults <= 0">
                <x-search.empty-state />
            </template>
        </div>

        <noscript>
            <x-search.noscript-fallback />
        </noscript>
    </x-stack>
</div>
