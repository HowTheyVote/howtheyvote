@props([
    'value' => 0,
    'total' => 0,
    'position' => null,
    'style' => null,
])

@php
    $ratio = $value / $total;
    $percentage = round($ratio * 100);
@endphp

<div
    {{ $attributes->bem('vote-result-chart__bar', $position) }}
    style="--ratio: {{ $ratio}}"
>
    @if ($style !== 'slim' && $percentage >= 10)
        <x-thumb :position="$position" />
    @endif

    @if ($style !== 'slim' && $percentage >= 5)
        {{ $percentage }}%
    @endif
</div>
