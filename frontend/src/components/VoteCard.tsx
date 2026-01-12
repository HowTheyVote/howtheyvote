import type { ComponentChild } from "preact";
import type { BaseVote } from "../api";
import { formatDate } from "../lib/dates";
import Card from "./Card";
import Tag from "./Tag";

type VoteCardProps = {
  vote: BaseVote;
  thumb?: ComponentChild;
};

export default function VoteCard({ vote, thumb }: VoteCardProps) {
  const meta = (
    <>
      {vote.topics.length > 0 &&
        vote.topics.map((topic) => <Tag key={topic.code}>{topic.label}</Tag>)}
      {vote.geo_areas.length > 0 &&
        vote.geo_areas.map((area) => <Tag key={area.code}>{area.label}</Tag>)}

      {formatDate(new Date(vote.timestamp))}
    </>
  );

  return (
    <Card
      title={vote.display_title}
      link={`/votes/${vote.id}`}
      meta={meta}
      thumb={thumb}
    />
  );
}
