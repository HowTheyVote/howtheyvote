<x-app
    title="{{ $votingList->display_title }} · Vote Result"
    :sharePicture="$votingList->share_picture_url"
    :sharePictureAlt="$votingList->share_picture_description"
>
    <x-base-layout>
        <x-stack space="xl">
            <x-stack space="xs">
                <h1 class="alpha">{{ $votingList->display_title }}</h1>
                <p>
                    <strong>
                        {{ $votingList->date->formatLocalized('%b %e, %Y') }}

                        @if ($votingList->vote)
                            ·
                            {{ Str::lower($votingList->vote->result->label) }}
                            <x-thumb style="circle" :result="$votingList->vote->result" />
                        @endif
                    </strong>
                </p>

                @if ($votingList->vote && $votingList->vote->summary)
                    <p>
                        {{ $votingList->vote->summary->excerpt }}
                        <a href="{{ route('voting-list.summary', [
                            'votingList' => $votingList,
                        ]) }}">
                            {{ __('voting-lists.summary.read-more') }}
                        </a>
                    </p>
                @endif

                @if ($votingList->vote && !$votingList->vote->isFinalVote())
                    <x-callout style="warning" :heading="__('voting-lists.non-final-callout.heading')">
                        @if ($votingList->vote->isAmendmentVote())
                            {{
                                __('voting-lists.non-final-callout.amendment', [
                                    'amendment' => lcfirst($votingList->vote->subtitle),
                                ])
                            }}
                        @endif

                        @if ($votingList->vote->isSeparateVote())
                            {{
                                __('voting-lists.non-final-callout.separate', [
                                    'separate' => lcfirst($votingList->vote->subtitle),
                                ])
                            }}
                        @endif

                        @if ($votingList->vote->finalVote?->url)
                        {!!
                            __('voting-lists.non-final-callout.text', [
                                'url' => $votingList->vote->finalVote->url,
                            ])
                        !!}
                        @endif
                    </x-callout>
                @endif
            </x-stack>

            @if ($votingList->vote && $votingList->vote->isFinalVote())
                <x-share-button
                    :title="$votingList->display_title"
                    :text="$votingList->display_title"
                    :url="route('voting-list.show', ['votingList' => $votingList])"
                    style="block"
                    size="lg"
                />
            @endif

            <x-vote-result-chart :stats="$votingList->stats"/>

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
                    <x-list
                        :truncate="true"
                        :show-more="__('voting-lists.members.show-more')"
                        :searchable="true"
                        :search-placeholder="__('voting-lists.members.search-placeholder')"
                    >
                        @foreach ($members as $member)
                            <x-member-list-item
                                :member="$member"
                                :position="$member->pivot->position"
                            />
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
                    <x-list
                        :truncate="true"
                        :show-more="__('voting-lists.countries.show-more')"
                        :searchable="true"
                        :search-placeholder="__('voting-lists.countries.search-placeholder')"
                    >
                        @foreach ($countries as $country => $stats)
                            <x-country-list-item
                                :country="\App\Enums\CountryEnum::make($country)"
                                :stats="$stats"
                            />
                        @endforeach
                    </x-list>
                </x-tab-panel>
            </x-tabs>

            <x-stack>
                @if ($votingList->vote && $votingList->vote->isFinalVote() && $votingList->vote->hasRelatedVotes())
                    <x-action-panel
                        :heading="__('voting-lists.related-votes-list.heading')"
                        :text="__('voting-lists.related-votes-list.text')"
                    >
                        <x-button
                            size="lg"
                            href="{{ route('voting-list.related', $votingList) }}"
                        >
                            {{ __('voting-lists.related-votes-list.button-label') }}
                        </x-button>
                    </x-action-panel>
                @endif

                <x-action-panel
                    :heading="__('voting-lists.download.heading')"
                    :text="__('voting-lists.download.text')"
                >
                    <x-button
                        size="lg"
                        href="{{ route('voting-list.csv', $votingList) }}"
                    >
                        {{ __('voting-lists.download.button-label') }}
                    </x-button>
                </x-action-panel>
            </x-stack>

        </x-stack>
    </x-base-layout>
</x-app>
