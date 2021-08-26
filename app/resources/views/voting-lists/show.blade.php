<x-app
    title="{{ $votingList->display_title }} · Vote Result"
    :sharePicture="$votingList->share_picture_url"
    :sharePictureAlt="$votingList->share_picture_description"
>
    <x-base-layout>
        <x-stack space="lg">
            <x-voting-list.header :votingList="$votingList" />

            @if ($votingList->vote && !$votingList->vote->isFinalVote())
                <div class="padding--h">
                    <x-wrapper>
                        <x-voting-list.callout :votingList="$votingList" />
                    </x-wrapper>
                </div>
            @endif

            <div class="padding--h">
                <x-wrapper>
                    <x-vote-result-chart :stats="$votingList->stats" />
                </x-wrapper>
            </div>

            <div class="padding--h">
                <x-wrapper>
                    <x-tabs>
                        <x-slot name="list">
                            <x-tab-button id="members" :selected="true">
                                {{ __('voting-lists.members.title') }}
                            </x-tab-button>
                            <x-tab-button id="groups">
                                {{ __('voting-lists.groups.title') }}
                            </x-tab-button>
                            <x-tab-button id="countries">
                                {{ __('voting-lists.countries.title') }}
                            </x-tab-button>
                        </x-slot>

                        <x-tab-panel id="members" :selected="true">
                            <x-voting-list.members-list :members="$members" />
                        </x-tab-panel>

                        <x-tab-panel id="groups">
                            <x-voting-list.groups-list :groups="$groups" />
                        </x-tab-panel>

                        <x-tab-panel id="countries">
                            <x-voting-list.countries-list :countries="$countries" />
                        </x-tab-panel>
                    </x-tabs>
                </x-wrapper>
            </div>

            <div class="padding--h">
                <x-wrapper>
                    <x-stack>
                        @if ($votingList->vote && $votingList->vote->isFinalVote() && $votingList->vote->hasRelatedVotes())
                            <x-voting-list.related-panel :votingList="$votingList" />
                        @endif

                        <x-voting-list.download-panel :votingList="$votingList" />
                    </x-stack>
                </x-wrapper>
            </div>
        </x-stack>
    </x-base-layout>
</x-app>
