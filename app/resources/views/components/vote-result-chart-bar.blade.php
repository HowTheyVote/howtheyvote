@props([
    'value' => 0,
    'total' => 0,
    'style' => null,
])

@php
    $ratio = $value / $total;
    $percentage = round($ratio * 100);
@endphp

<div
    class="vote-result-chart__bar vote-result-chart__bar--{{ $style }}"
    style="--ratio: {{ $ratio}}"
>
    {{ $value }}

    @if ($percentage > 5)
        / {{ $percentage }}%
    @endif
</div>
