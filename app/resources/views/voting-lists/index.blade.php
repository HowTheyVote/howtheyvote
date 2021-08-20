<x-app title="Votes">
    <x-base-layout>
        <x-stack>
            <h1 class="alpha">Votes</h1>

            <x-stack space="xs">
                @foreach ($sessions as $session)
                    <h2 class="beta">{{ $session->display_title }}</h2>

                    @foreach ($session->matchedFinalVotes as $vote)
                        <x-vote-card :vote="$vote" />
                    @endforeach
                @endforeach
            </x-stack>
        </x-stack>
    </x-base-layout>
</x-app>
