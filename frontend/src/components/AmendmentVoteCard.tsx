import type { RelatedVote } from "../api";
import { formatDate } from "../lib/dates";
import Card from "./Card";
import Thumb from "./Thumb";

type AmendmentVoteCardProps = {
  vote: RelatedVote;
};

export default function AmendmentVoteCard({ vote }: AmendmentVoteCardProps) {
  return (
    <Card
      title={vote.description}
      link={`/votes/${vote.id}`}
      meta={formatDate(new Date(vote.timestamp))}
      thumb={vote.result && <Thumb style="circle" result={vote.result} />}
    />
  );
}
