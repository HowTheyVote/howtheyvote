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
            <strong>For: {{ $stats['by_position']['FOR'] }}</strong>
            <x-thumb modifiers="for" />
        </span>

        |

        <span class="text--red">
            <strong>Against: {{ $stats['by_position']['AGAINST'] }}</strong>
            <x-thumb modifiers="against" />
        </span>

        |

        <span class="text--blue">
            <strong>Abstentions: {{ $stats['by_position']['ABSTENTION'] }}</strong>
            <x-thumb modifiers="abstention" />
        </span>

        |

        In total, <strong>{{ $stats['voted'] }} MEPs</strong> voted.
        <strong>{{ $stats['active'] - $stats['voted'] }} MEPs</strong> didn’t vote.
    </p>
</x-stack>
