<x-app title="{{ $votingList->displayTitle }} · Vote Result">
    <x-wrapper>
        <x-stack space="lg">
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

            <x-tabs>
                <x-slot name="list">
                    <x-tab-button id="members" :selected="true">MEPs</x-tab-button>
                    <x-tab-button id="groups">Political Groups</x-tab-button>
                    <x-tab-button id="countries">Countries</x-tab-button>
                </x-slot>

                <x-tab-panel id="members">
                    <x-list :truncate="10">
                        @foreach ($members as $member)
                            <x-member-list-item :member="$member" :position="$member->pivot->position" />
                        @endforeach
                    </x-list>
                </x-tab-panel>

                <x-tab-panel id="groups">
                    <x-list>
                        @foreach ($groups as $group)
                            <x-group-list-item :group="$group" :stats="$group->stats" />
                        @endforeach
                    </x-list>
                </x-tab-panel>

                <x-tab-panel id="countries">
                    <x-list :truncate="true">
                        @foreach ($countries as $country => $stats)
                            <x-country-list-item :country="\App\Enums\CountryEnum::make($country)" :stats="$stats" />
                        @endforeach
                    </x-list>
                </x-tab-panel>
            </x-tabs>
        </x-stack>
    </x-wrapper>
</x-app>
