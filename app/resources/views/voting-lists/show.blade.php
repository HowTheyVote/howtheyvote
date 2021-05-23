<x-app title="{{ $votingList->displayTitle }} - Vote Result">
    <x-wrapper>
        <x-stack space="xs">
            <h1 class="alpha">{{ $votingList->display_title }}</h1>
            <p>
                {{ $votingList->date->formatLocalized('%b %e, %Y') }}

                @if ($votingList->vote)
                    –
                    {{ Str::lower($votingList->vote->result->label) }}
                    <x-thumb style="circle" :result="$votingList->vote->result" />
                @endif
            </p>

            <x-vote-result-chart :stats="$votingList->stats" />
        </x-stack>


    </x-wrapper>

    <x-avatar url="https://www.europarl.europa.eu/mepphoto/197433.jpg" />
    <x-avatar url="https://www.europarl.europa.eu/mepphoto/1911.jpg" />
    <x-avatar url="https://www.europarl.europa.eu/mepphoto/28229.jpg" />
</x-app>
