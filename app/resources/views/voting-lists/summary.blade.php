<x-app title="{{ $votingList->displayTitle }} · Summary">
    <x-base-layout>
        <x-stack>
            <h1 class="alpha">{{ $votingList->display_title }}</h1>

            <x-markdown>
                {{ $summary->text }}
            </x-markdown>

            <x-callout>
                <p>
                    {!! __('votes.summary.copyright', [
                        'url' => $summary->external_url,
                        'year' => $summary->created_at->format('Y'),
                    ]) !!}
                </p>
            </x-callout>
        </x-stack>
    </x-base-layout>
</x-app>
