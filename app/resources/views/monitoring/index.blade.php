<x-app title="Monitoring">
    <x-base-layout>
        <x-stack>
            <h1>VotingLists</h1>
            <ul>
                @foreach ($votingLists as $votingList)
                    <li>
                        <a href="{{route('monitoring.showLists', [
                            'votingList' => $votingList])}}">
                                {{ $votingList->id }} - {{ $votingList->description }}
                        </a>
                    </li>
                @endforeach
            </ul>
            <h1>Votes</h1>
            <ul>
                @foreach ($votes as $vote)
                    <li>
                        <a href="{{route('monitoring.showVotes', [
                            'vote' => $vote])}}">
                            {{ $vote->id }} - Subject: {{ $vote->subject }} - Collection: {{ $vote->vote_collection_id }} - Reference: {{ $vote->reference }} - Notes: {{ $vote->notes }}
                        </a>
                    </li>
                @endforeach
            </ul>
        </x-stack>
    </x-base-layout>
</x-app>
