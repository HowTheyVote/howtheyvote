@props(['stats' => null])

<div class="vote-result-chart">
    <x-vote-result-chart-bar
        :value="$stats['by_position']['FOR']"
        :total="$stats['voted']"
        style="for"
    />

    <x-vote-result-chart-bar
        :value="$stats['by_position']['AGAINST']"
        :total="$stats['voted']"
        style="against"
    />

    <x-vote-result-chart-bar
        :value="$stats['by_position']['ABSTENTION']"
        :total="$stats['voted']"
        style="abstention"
    />
</div>
