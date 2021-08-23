<article class="vote-card">
    <a x-bind:href="`/votes/${vote.id}`">
        <x-thumb
            class="vote-card__thumb"
            result="adopted"
            style="circle"
            x-show="vote.result === 'adopted'"
        />

        <x-thumb
            class="vote-card__thumb"
            result="rejected"
            style="circle"
            x-show="vote.result === 'rejected'"
        />

        <div>
            <strong x-html="vote._formatted.display_title"></strong>
            <p x-text="formatDate(vote.date)"></p>
        </div>
    </a>
</article>
