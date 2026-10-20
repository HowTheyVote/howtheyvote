import type { MemberVote } from "../api";
import Disclosure from "./Disclosure";
import Thumb from "./Thumb";

import "./VotePositionLegend.css";

const positions: Array<{
  position: MemberVote["position"];
  label: string;
  description: string;
}> = [
  {
    position: "FOR",
    label: "For",
    description: "The MEP voted in favour.",
  },
  {
    position: "AGAINST",
    label: "Against",
    description: "The MEP voted against.",
  },
  {
    position: "ABSTENTION",
    label: "Abstention",
    description:
      "The MEP took part in the vote and chose neither for nor against.",
  },
  {
    position: "DID_NOT_VOTE",
    label: "Did not vote",
    description:
      "The MEP did not take part in this vote. This does not necessarily mean they were absent.",
  },
];

export default function VotePositionLegend() {
  return (
    <Disclosure title="What do the voting symbols mean?">
      <dl class="vote-position-legend text--sm">
        {positions.map(({ position, label, description }) => (
          <div key={position}>
            <dt class="vote-position-legend__label">
              <span aria-hidden="true">
                <Thumb position={position} style="circle" />
              </span>
              <strong>{label}</strong>
            </dt>
            <dd class="vote-position-legend__description">{description}</dd>
          </div>
        ))}
      </dl>
    </Disclosure>
  );
}
