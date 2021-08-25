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
    {{ $attributes->bem('vote-result-chart__bar', [
        $style,
        $position,
        'small' => $percentage < 10,
        'medium' => $percentage >= 10 && $percentage < 15,
    ]) }}
    style="--ratio: {{ $ratio}}"
>
    <x-thumb class="vote-result-chart__thumb" :position="$position" />
    <span class="vote-result-chart__percentage">{{ $percentage }}%</span>
</div>
