<x-app title="Monitoring" padding="true">
    <ul>
        @foreach ($votingLists as $votingList)
            <li>{{ $votingList->id }} - {{ $votingList->description }}</li>
        @endforeach
    </ul>
</x-app>
