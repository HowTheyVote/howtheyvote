import type { RelatedVote } from "../api";
import { formatDate } from "../lib/dates";
import Card from "./Card";

type AmendmentVoteCardProps = {
  vote: RelatedVote;
};

export default function AmendmentVoteCard({ vote }: AmendmentVoteCardProps) {
  return (
    <Card
      title={vote.description}
      link={`/votes/${vote.id}`}
      meta={formatDate(new Date(vote.timestamp))}
    />
  );
}
