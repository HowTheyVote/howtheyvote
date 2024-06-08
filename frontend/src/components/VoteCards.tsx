import { BaseVote } from "../api";
import { formatDate } from "../lib/dates";
import Stack from "./Stack";
import VoteCard from "./VoteCard";

import "./VoteCards.css";

type VoteCardsProps = {
  votes: Array<BaseVote>;
  groupByDate?: boolean;
};

type GroupProps = {
  votes: Array<BaseVote>;
  title?: string;
};

function Group({ votes, title }: GroupProps) {
  return (
    <Stack space="sm">
      {title && <h2 class="delta">{title}</h2>}

      {votes.map((vote: BaseVote) => (
        <VoteCard vote={vote} />
      ))}
    </Stack>
  );
}

export default function VoteCards({ votes, groupByDate }: VoteCardsProps) {
  if (!groupByDate) {
    return (
      <div class="vote-cards">
        <Group votes={votes} />
      </div>
    );
  }

  const groups = new Map<string, Array<BaseVote>>();

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
        <Group votes={votes} title={formattedDate} />
      ))}
    </div>
  );
}
