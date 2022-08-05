@props([
    'endpoint' => null,
    'index' => null,
    'apiKey' => null,
    'memberId' => null,
])

@once
    @push('head')
        <link rel="preconnect" href="{{ $endpoint }}" />
    @endpush
@endonce

<div
    {{ $attributes->bem('search-results-page') }}
    x-data="searchResultsPage({{ json_encode([
        'endpoint' => $endpoint,
        'index' => $index,
        'apiKey' => $apiKey,
        'memberId' => $memberId,
    ]) }})"
>
    <x-stack>
        <template x-if="hasQuery && totalNumberOfResults > 0">
            <x-search-results-page.results-count />
        </template>

        <template x-if="totalNumberOfResults > 0">
            <x-search-results-page.results />
        </template>

        <template x-if="hasMoreResults">
            <x-search-results-page.load-more-button />
        </template>

        <template x-if="initialLoadCompleted && hasQuery && totalNumberOfResults <= 0">
            <x-search-results-page.empty-state />
        </template>

        <noscript>
            <x-search-results-page.noscript-fallback />
        </noscript>

        <div x-show="!initialLoadCompleted" class="text--center">
            <x-loading-spinner />
        </div>
    </x-stack>
</div>
