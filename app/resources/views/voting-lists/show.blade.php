<x-app title="{{ $votingList->displayTitle }} · Vote Result">
    <x-wrapper>
        <x-stack>
            <x-stack space="xs">
                <h1 class="alpha">{{ $votingList->display_title }}</h1>
                <p>
                    {{ $votingList->date->formatLocalized('%b %e, %Y') }}

                    @if ($votingList->vote)
                        ·
                        {{ Str::lower($votingList->vote->result->label) }}
                        <x-thumb style="circle" :result="$votingList->vote->result" />
                    @endif
                </p>

                <x-vote-result-chart :stats="$votingList->stats"/>
            </x-stack>

            <x-list>
                @foreach ($countries as $country => $stats)
                    <x-country-list-item :country="\App\Enums\CountryEnum::make($country)" :stats="$stats" />
                @endforeach
            </x-list>

            <x-list>
                @foreach ($groups as $group)
                    <x-group-list-item :group="$group" :stats="$group->stats" />
                @endforeach
            </x-list>

            <x-list>
                @foreach ($members as $member)
                    <x-member-list-item :member="$member" :position="$member->pivot->position" />
                @endforeach
            </x-list>
        </x-stack>
    </x-wrapper>


</x-app>
