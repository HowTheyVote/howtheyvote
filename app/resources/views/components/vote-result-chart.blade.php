@props([
    'stats' => null,
    'style' => null,
])

<x-stack class="stack--xxs">
    <div {{ $attributes->bem('vote-result-chart', $style) }}>
        @if ($stats['by_position']['FOR'] > 0)
        <x-vote-result-chart-bar
            :value="$stats['by_position']['FOR']"
            :total="$stats['voted']"
            :style="$style"
            position="for"
        />
        @endif

        @if ($stats['by_position']['AGAINST'] > 0)
        <x-vote-result-chart-bar
            :value="$stats['by_position']['AGAINST']"
            :total="$stats['voted']"
            :style="$style"
            position="against"
        />
        @endif

        @if ($stats['by_position']['ABSTENTION'] > 0)
        <x-vote-result-chart-bar
            :value="$stats['by_position']['ABSTENTION']"
            :total="$stats['voted']"
            :style="$style"
            position="abstention"
        />
        @endif
    </div>

    @if ($style !== 'slim')
        <p class="text--sm">
            @lang('voting-lists.for'): <strong>{{ $stats['by_position']['FOR'] }}</strong>.
            @lang('voting-lists.against'): <strong>{{ $stats['by_position']['AGAINST'] }}</strong>.
            @lang('voting-lists.abstentions'): <strong>{{ $stats['by_position']['ABSTENTION'] }}</strong>.
            @lang('voting-lists.share-picture.summary', [
                'voted' => $stats['voted'],
                'did-not-vote' => $stats['by_position']['NOVOTE'],
            ])
        </p>
    @endif
</x-stack>
