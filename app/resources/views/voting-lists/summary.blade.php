<x-app title="{{ $votingList->displayTitle }} · Summary">
    <x-base-layout>
        <x-stack>
            <x-voting-list.header
                :votingList="$votingList"
                :minimal="true"
            />

            <div class="padding--h">
                <x-wrapper>
                    <x-markdown>
                        {{ $summary->text }}
                    </x-markdown>
                </x-wrapper>
            </div>

            <div class="padding--h">
                <x-wrapper>
                    <x-callout>
                        <p>
                            {!! __('votes.summary.copyright', [
                                'url' => $summary->external_url,
                                'year' => $summary->created_at->format('Y'),
                            ]) !!}
                        </p>
                    </x-callout>
                </x-wrapper>
            </div>
        </x-stack>
    </x-base-layout>
</x-app>
