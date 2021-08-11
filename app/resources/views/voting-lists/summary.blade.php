<x-app title="{{ $votingList->displayTitle }} · Related Votes">
    <x-wrapper>
        <x-stack>
            <h1 class="alpha">{{ $votingList->display_title }}</h1>

            <x-markdown>
                {{ $summary->text }}
            </x-markdown>
        </x-stack>
    </x-wrapper>
</x-app>
