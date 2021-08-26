<x-app
    title="{{ $member->full_name }} · Votes Casted"
>
    <x-base-layout>
        <x-stack>
            <x-member-card :member="$member" />
            <section>
                <x-stack space="xs">
                    @foreach ($votingLists as $votingList)
                        <x-vote-card
                            :vote="$votingList->vote"
                            :position="Str::lower($votingList->pivot->position->label)"
                        />
                    @endforeach
                </x-stack>
            </section>
        </x-stack>
    </x-base-layout>
</x-app>
