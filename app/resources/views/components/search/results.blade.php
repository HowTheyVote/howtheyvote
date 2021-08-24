<div x-ref="results">
    <template x-if="!hasQuery">
        <x-stack space="lg">
            <template
                x-for="session in resultsGroupedBySession"
                x-bind:key="session.id"
            >
                <x-stack space="sm">
                    <h2 class="beta" x-text="session.displayTitle"></h2>
                    <template x-for="vote in session.votes" x-bind:key="vote.id">
                        <x-search.result />
                    </template>
                </x-stack>
            </template>
        </x-stack>
    </template>

    <template x-if="hasQuery">
        <x-stack space="sm">
            <template x-for="vote in results" x-bind:key="vote.id">
                <x-search.result />
            </template>
        </x-stack>
    </template>
</div>
