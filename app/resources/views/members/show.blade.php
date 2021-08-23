<x-app
    title="{{ $member->full_name }} · Votes Casted"
>
    <x-base-layout>
        <x-stack>
            <h1 class="alpha">{{ $member->full_name }}</h1>
            <x-member-card :member="$member" />
            <x-stack space="xs">
                @foreach ($votingLists as $votingList)
                    <x-vote-card
                        :vote="$votingList->vote"
                        :position="Str::lower($votingList->pivot->position->label)"
                    />
                @endforeach
            </x-stack>
        </x-stack>
    </x-base-layout>
</x-app>
