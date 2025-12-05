import type { ComponentChild } from "preact";
import type { BaseVote } from "../api";
import { formatDate } from "../lib/dates";
import Tag from "./Tag";

import "./VoteCard.css";

type VoteCardProps = {
  vote: BaseVote;
  thumb?: ComponentChild;
};

export default function VoteCard({ vote, thumb }: VoteCardProps) {
  return (
    <article class="vote-card">
      <div class="vote-card__text">
        <h2 class="vote-card__title">
          <a href={`/votes/${vote.id}`}>{vote.display_title}</a>
        </h2>
        <div class="vote-card__meta">
          {vote.geo_areas.length > 0 &&
            vote.geo_areas.map((area) => (
              <Tag key={area.code}>{area.label}</Tag>
            ))}
          {formatDate(new Date(vote.timestamp))}
        </div>
      </div>
      {thumb && <div class="vote-card__thumb">{thumb}</div>}
    </article>
  );
}
