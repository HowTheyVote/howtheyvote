@props(['stats' => null])

<x-stack class="stack--xxs">
    <div class="vote-result-chart">
        <x-vote-result-chart-bar
            :value="$stats['by_position']['FOR']"
            :total="$stats['voted']"
            position="for"
        />

        <x-vote-result-chart-bar
            :value="$stats['by_position']['AGAINST']"
            :total="$stats['voted']"
            position="against"
        />

        <x-vote-result-chart-bar
            :value="$stats['by_position']['ABSTENTION']"
            :total="$stats['voted']"
            position="abstention"
        />
    </div>

    <p class="text--xs">
        <span class="text--green">
            <strong>@lang('votes.for'): {{ $stats['by_position']['FOR'] }}</strong>
            <x-thumb modifiers="for" />
        </span>

        |

        <span class="text--red">
            <strong>@lang('votes.against'): {{ $stats['by_position']['AGAINST'] }}</strong>
            <x-thumb modifiers="against" />
        </span>

        |

        <span>
            <strong>@lang('votes.abstentions'): {{ $stats['by_position']['ABSTENTION'] }}</strong>
            <x-thumb modifiers="abstention" />
        </span>

        |

        @lang('votes.share-picture.summary', [
            'voted' => $stats['voted'],
            'did-not-vote' => $stats['active'] - $stats['voted']
        ])
    </p>
</x-stack>
