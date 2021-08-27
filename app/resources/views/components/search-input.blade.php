<x-input
    x-data="{}"
    x-model="$store.searchQuery"
    type="search"
    :placeholder="__('components.search-input.placeholder')"
    size="lg"
    autofocus
    name="q"
    style="elevated"
    {{ $attributes }}
/>
