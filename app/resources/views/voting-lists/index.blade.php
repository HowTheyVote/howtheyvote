<x-app title="Votes" padding="true">
    <x-wrapper>
        <x-stack>
            <h1 class="alpha">Votes</h1>

            <x-stack space="xs">
                @foreach ($sessions as $session)
                    <h2 class="beta">{{ $session->display_title }}</h2>

                    @foreach ($session->primaryVotes as $vote)
                        <x-vote-card :vote="$vote" />
                    @endforeach
                @endforeach
            </x-stack>
        </x-stack>
    </x-wrapper>
</x-app>
