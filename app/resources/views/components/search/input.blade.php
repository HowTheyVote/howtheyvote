<x-input
    type="search"
    :placeholder="__('components.search.placeholder')"
    x-model="query"
    x-on:input="search()"
    size="lg"
    autofocus
/>
