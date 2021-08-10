@props(['vote' => null])

<article {{ $attributes->bem('vote-card') }}>
    <a href="{{ route('voting-list.show', ['votingList' => $vote->votingList]) }}">
        <x-thumb
            class="vote-card__thumb"
            :result="$vote->result"
            style="circle"
        />
        <div>
            <strong>{{ $vote->subtitle }}</strong><br>

            @if ($vote->subheading)
                <p>{{ $vote->subheading }}</p>
            @endif
        </div>
    </a>
</article>
