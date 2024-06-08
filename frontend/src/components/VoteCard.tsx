import type { BaseVote } from "../api";
import { formatDate } from "../lib/dates";
import Tag from "./Tag";

import "./VoteCard.css";

type VoteCardProps = {
  vote: BaseVote;
};

export default function VoteCard({ vote }: VoteCardProps) {
  return (
    <article class="vote-card">
      <h2 class="vote-card__title">
        <a href={`/votes/${vote.id}`}>{vote.display_title}</a>
      </h2>
      <div class="vote-card__meta">
        {vote.is_featured && <Tag style="featured">Featured</Tag>}
        {vote.geo_areas.length > 0 &&
          vote.geo_areas.map((area) => <Tag key={area.code}>{area.label}</Tag>)}
        {formatDate(new Date(vote.timestamp))}
      </div>
    </article>
  );
}
