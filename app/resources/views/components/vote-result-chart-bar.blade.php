@props([
    'value' => 0,
    'total' => 0,
    'position' => null,
])

@php
    $ratio = $value / $total;
    $percentage = round($ratio * 100);
@endphp

<div
    {{ $attributes->bem('vote-result-chart__bar', $position) }}
    style="--ratio: {{ $ratio}}"
>
    @if ($percentage >= 10)
        <x-thumb :position="$position" />
    @endif

    @if ($percentage >= 5)
        {{ $percentage }}%
    @endif
</div>
