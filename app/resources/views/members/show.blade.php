<x-app
    title="{{ $member->full_name }} · Votes Casted"
>
    <x-base-layout>
        <h1 class="alpha">{{ $member->full_name }}</h1>
        <x-member-card :member="$member" />
        <x-stack>
            @foreach ($votes as $vote)
                <x-list-item
                    :title="$vote->display_title"

                />
            @endforeach
        </x-stack>
    </x-base-layout>
</x-app>
