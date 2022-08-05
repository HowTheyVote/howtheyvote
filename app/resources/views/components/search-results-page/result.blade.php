<article class="vote-card">
    <a x-bind:href="`/votes/${vote.id}`">
        <x-thumb
            class="vote-card__thumb"
            result="adopted"
            style="circle"
            x-show="!memberId && vote.result === 'adopted'"
        />

        <x-thumb
            class="vote-card__thumb"
            result="rejected"
            style="circle"
            x-show="!memberId && vote.result === 'rejected'"
        />

        <x-thumb
            class="vote-card__thumb"
            position="for"
            style="circle"
            x-show="memberId && vote.members[memberId] === 'FOR'"
        />

        <x-thumb
            class="vote-card__thumb"
            position="against"
            style="circle"
            x-show="memberId && vote.members[memberId] === 'AGAINST'"
        />

        <x-thumb
            class="vote-card__thumb"
            position="abstention"
            style="circle"
            x-show="memberId && vote.members[memberId] === 'ABSTENTION'"
        />

        <x-thumb
            class="vote-card__thumb"
            position="novote"
            style="circle"
            x-show="memberId && vote.members[memberId] === 'NOVOTE'"
        />

        <div>
            <strong x-html="vote._formatted.display_title"></strong>
            <p x-text="formatDate(vote.date)"></p>
        </div>
    </a>
</article>
