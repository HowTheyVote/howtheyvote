import type { RelatedVote } from "../api";
import { formatDate } from "../lib/dates";
import AmendmentVoteCard from "./AmendmentVoteCard";
import Stack from "./Stack";

import "./VoteCards.css";

type AmendmentVoteCardsProps = {
  votes: Array<RelatedVote>;
  groupByDate?: boolean;
};

type GroupProps = {
  votes: Array<RelatedVote>;
  // To group by political Group later
  title?: string;
};

function Group({ votes, title }: GroupProps) {
  return (
    <Stack space="sm">
      {title && <h2 class="delta">{title}</h2>}

      {votes.map((vote: RelatedVote) => (
        <AmendmentVoteCard key={vote.id} vote={vote} />
      ))}
    </Stack>
  );
}

export default function AmendmentVoteCards({
  votes,
  groupByDate,
}: AmendmentVoteCardsProps) {
  if (!groupByDate) {
    return (
      <div class="vote-cards">
        <Group votes={votes} />
      </div>
    );
  }

  const groups = new Map<string, Array<RelatedVote>>();

  for (const vote of votes) {
    const key = formatDate(new Date(vote.timestamp));

    if (!key) {
      continue;
    }

    const otherVotes = groups.get(key) || [];
    groups.set(key, [...otherVotes, vote]);
  }

  return (
    <div class="vote-cards">
      {Array.from(groups.entries()).map(([formattedDate, votes]) => (
        <Group key={formattedDate} votes={votes} title={formattedDate} />
      ))}
    </div>
  );
}
