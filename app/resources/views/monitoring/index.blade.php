<x-app title="Monitoring">
    <x-base-layout>
        <ul>
            @foreach ($votingLists as $votingList)
                <li>{{ $votingList->id }} - {{ $votingList->description }}</li>
            @endforeach
        </ul>
    </x-base-layout>
</x-app>
