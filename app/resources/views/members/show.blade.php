<x-app
    title="{{ $member->full_name }} · Votes Casted"
>
    <x-base-layout>
        <x-stack space="lg">
            <x-member.header :member="$member" :group="$group" />

            <section class="padding--h">
                <x-wrapper>
                    <x-stack space="sm">
                        @foreach ($votingLists as $votingList)
                            <x-vote-card
                                :vote="$votingList->vote"
                                :position="Str::lower($votingList->pivot->position->label)"
                            />
                        @endforeach
                    </x-stack>
                </x-wrapper>
            </section>
        </x-stack>
    </x-base-layout>
</x-app>
