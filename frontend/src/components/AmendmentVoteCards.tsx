import type { RelatedVote } from "../api";
import AmendmentVoteCard from "./AmendmentVoteCard";
import Stack from "./Stack";

import "./VoteCards.css";

type AmendmentVoteCardsProps = {
  votes: Array<RelatedVote>;
};

type GroupProps = {
  votes: Array<RelatedVote>;
};

function Group({ votes }: GroupProps) {
  return (
    <Stack space="sm">
      {votes.map((vote: RelatedVote) => (
        <AmendmentVoteCard key={vote.id} vote={vote} />
      ))}
    </Stack>
  );
}

export default function AmendmentVoteCards({ votes }: AmendmentVoteCardsProps) {
  return (
    <div class="vote-cards">
      <Group votes={votes} />
    </div>
  );
}
