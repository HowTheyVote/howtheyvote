import type { MemberVote, VotePositionCounts } from "../api";
import { bem } from "../lib/bem";
import Thumb from "./Thumb";

import "./VoteResultChart.css";

type VoteResultChartProps = {
  stats: VotePositionCounts;
  includeNoShows?: boolean;
  style?: "slim";
};

type BarProps = {
  value: number;
  total: number;
  position: MemberVote["position"];
};

type SummaryProps = {
  stats: VotePositionCounts;
};

function Bar({ value, total, position }: BarProps) {
  const ratio = Math.round((value / total) * 1000) / 1000;

  if (value === 0) {
    return null;
  }

  const percentage = Math.round(ratio * 100);
  const style = position.toLowerCase().replaceAll("_", "-");

  return (
    <div
      className={bem("vote-result-chart__bar", style)}
      style={{ "--ratio": ratio }}
      title={`${value} MEPs voted ${position} (${percentage}%)`}
    >
      <span className="vote-result-chart__label">
        <Thumb position={position} className="vote-result-chart__thumb" />
        <span class="vote-result-chart__percentage">{percentage}%</span>
      </span>
    </div>
  );
}

function Summary({ stats }: SummaryProps) {
  const total = stats.FOR + stats.AGAINST + stats.ABSTENTION;
  const percentageFor = Math.round((stats.FOR / total) * 100);
  const percentageAgainst = Math.round((stats.AGAINST / total) * 100);
  const percentageAbstention = Math.round((stats.ABSTENTION / total) * 100);

  return (
    <p class="text--sm text--light">
      For: <strong>{stats.FOR}</strong>
      <span class="visually-hidden">({percentageFor} %)</span>. Against:{" "}
      <strong>{stats.AGAINST}</strong>
      <span class="visually-hidden">({percentageAgainst} %)</span>. Abstentions:{" "}
      <strong>{stats.ABSTENTION}</strong>
      <span class="visually-hidden">({percentageAbstention} %)</span>. In total,{" "}
      <strong>{total} MEPs</strong> voted.{" "}
      <strong>{stats.DID_NOT_VOTE} MEPs</strong> didn’t vote.
    </p>
  );
}

export default function VoteResultChart({
  stats,
  style,
  includeNoShows,
}: VoteResultChartProps) {
  let total = stats.FOR + stats.AGAINST + stats.ABSTENTION;
  if (includeNoShows) total += stats.DID_NOT_VOTE;
  return (
    <figure className={bem("vote-result-chart", style)}>
      <div class="vote-result-chart__bars" aria-hidden="true">
        <Bar position="FOR" value={stats.FOR} total={total} />
        <Bar position="AGAINST" value={stats.AGAINST} total={total} />
        <Bar position="ABSTENTION" value={stats.ABSTENTION} total={total} />
        { includeNoShows &&         <Bar position="DID_NOT_VOTE" value={stats.DID_NOT_VOTE} total={total} />
}
      </div>
      <figcaption class={style === "slim" ? "visually-hidden" : undefined}>
        <Summary stats={stats} />
      </figcaption>
    </figure>
  );
}
