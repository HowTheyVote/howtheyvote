@props([
    'vote' => null,
    'heading' => null,
    'text' => null,
    ])

<article {{ $attributes->bem('vote-card') }}>
    <a href="{{ route('voting-list.show', $vote->votingList) }}">
        <x-thumb
            class="vote-card__thumb"
            :result="$vote->result"
            style="circle"
        />
        <div>
            <strong>{{ $heading ? $heading : $vote->display_title }}</strong>
            <p>{{ $text === null ? $vote->formatted_date : $text }}</p>
        </div>
    </a>
</article>
