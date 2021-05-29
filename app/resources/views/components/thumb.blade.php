@props([
    'position' => null,
    'result' => null,
    'style' => null
])

@php
    if (is_a($position, \App\Enums\VotePositionEnum::class))
    {
        $position = Str::lower($position->label);
    }

    if (is_a($result, \App\Enums\VoteResultEnum::class))
    {
        $result = Str::lower($result->label);
    }
@endphp

<span {{ $attributes->bem('thumb', [$position, $result, $style]) }}>
    <svg aria-hidden="true"><use href="/assets/icons.svg#thumb" /></svg>
</span>
