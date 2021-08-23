<x-app title="{{ $votingList->displayTitle }} - Share Picture">
    <x-share-picture>
        <x-stack space="sm">
            <x-stack space="xxs">
                <h1 class="alpha share-picture__title">
                    {{ $votingList->display_title }}
                </h1>
                <p class="text--sm share-picture__result">
                    @lang('voting-lists.share-picture.subtitle', [
                        'date' => $votingList->date->formatLocalized('%b %e, %Y'),
                    ])

                    @if ($votingList->vote)
                        <strong>
                            {{ ucfirst($votingList->result_string) }}
                        </strong>
                        <x-thumb style="circle" :result="$votingList->result" />
                    @endif
                </p>
            </x-stack>
            <x-vote-result-chart :stats="$votingList->stats" />
        </x-stack>

        <x-slot name="footer">
            {{ __('voting-lists.share-picture.footer') }}<br>
            <strong>{{ $shortDisplayUrl }}</strong>
        </x-slot>
    </x-share-picture>
</x-app>
