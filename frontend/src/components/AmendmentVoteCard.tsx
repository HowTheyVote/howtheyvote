import type { RelatedVote } from "../api";
import { formatDate } from "../lib/dates";

import "./VoteCard.css";

type AmendmentVoteCardProps = {
  vote: RelatedVote;
};

export default function AmendmentVoteCard({ vote }: AmendmentVoteCardProps) {
  return (
    <article class="vote-card">
      <div class="vote-card__text">
        <h2 class="vote-card__title">
          <a href={`/votes/${vote.id}`}>{vote.description}</a>
        </h2>
        <div class="vote-card__meta">
          {formatDate(new Date(vote.timestamp))}
        </div>
      </div>
    </article>
  );
}
