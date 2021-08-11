<x-app title="Votes">
    <x-wrapper>
        <x-stack>
            <h1 class="alpha">Votes</h1>

            <x-stack space="xs">
                @foreach ($votingLists as $votingList)
                    <x-vote-card
                        :vote="$votingList->vote"
                    />
                @endforeach
            </x-stack>

        </x-stack>
    </x-wrapper>
</x-app>
