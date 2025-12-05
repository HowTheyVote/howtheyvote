import type { FunctionComponent } from "preact";
import type { BaseVote, RelatedVote } from "../api";
import { formatDate } from "../lib/dates";
import Stack from "./Stack";

type VoteType = BaseVote | RelatedVote;

type VoteCardsProps<T extends VoteType> = {
  votes: Array<T>;
  groupByDate?: boolean;
  children: FunctionComponent<{ vote: T }>;
};

type GroupProps<T extends VoteType> = {
  votes: Array<T>;
  title?: string;
  children: FunctionComponent<{ vote: T }>;
};

function Group<T extends VoteType>({
  votes,
  title,
  children: Component,
}: GroupProps<T>) {
  return (
    <Stack space="sm">
      {title && <h2 class="delta">{title}</h2>}

      {votes.map((vote: T) => (
        <Component key={vote.id} vote={vote} />
      ))}
    </Stack>
  );
}

export default function VoteCards<T extends VoteType>({
  votes,
  groupByDate,
  children,
}: VoteCardsProps<T>) {
  if (!groupByDate) {
    return <Group votes={votes}>{children}</Group>;
  }

  const groups = new Map<string, Array<T>>();

  for (const vote of votes) {
    const key = formatDate(new Date(vote.timestamp));

    if (!key) {
      continue;
    }

    const otherVotes = groups.get(key) || [];
    groups.set(key, [...otherVotes, vote]);
  }

  return (
    <Stack space="xl">
      {Array.from(groups.entries()).map(([formattedDate, votes]) => (
        <Group key={formattedDate} votes={votes} title={formattedDate}>
          {children}
        </Group>
      ))}
    </Stack>
  );
}
