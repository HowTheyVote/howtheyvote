@props(['stats' => null])

<div class="vote-result-chart">
    <x-vote-result-chart-bar
        :value="$stats['by_position']['FOR']"
        :total="$stats['active']"
        style="for"
    />

    <x-vote-result-chart-bar
        :value="$stats['by_position']['AGAINST']"
        :total="$stats['active']"
        style="against"
    />

    <x-vote-result-chart-bar
        :value="$stats['by_position']['ABSTENTION']"
        :total="$stats['active']"
        style="abstention"
    />

    <x-vote-result-chart-bar
        :value="$stats['active'] - $stats['voted']"
        :total="$stats['active']"
        style="absent"
    />
</div>
