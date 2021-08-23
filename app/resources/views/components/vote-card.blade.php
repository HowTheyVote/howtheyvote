@props([
    'vote' => null,
    'heading' => null,
    'text' => null,
    'position' => null,
    ])

@php
    $position = $position == null ? $vote->result: $position;
@endphp

<article {{ $attributes->bem('vote-card') }}>
    <a href="{{ route('voting-list.show', $vote->votingList) }}">
        <x-thumb
            class="vote-card__thumb"
            :result="$position"
            style="circle"
        />
        <div>
            <strong>{{ $heading ? $heading : $vote->display_title }}</strong>
            <p>{{ $text !== null ? $text : $vote->votingList->formatted_date }}</p>
        </div>
    </a>
</article>
