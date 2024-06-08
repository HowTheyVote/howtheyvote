import { Vote } from "../api";
import { formatDate } from "../lib/dates";
import CCLogo from "./CCLogo";
import VoteResultChart from "./VoteResultChart";

import "./VoteSharepic.css";

type VoteSharepicProps = {
  vote: Vote;
};

export default function VoteSharepic({ vote }: VoteSharepicProps) {
  return (
    <div class="vote-sharepic">
      <main class="vote-sharepic__content">
        <header class="mb--sm">
          <h1 class="beta vote-sharepic__title mb-xxs">{vote.display_title}</h1>
          <p class="text--sm vote-sharepic__subtitle">
            {formatDate(vote.timestamp)}
            {vote.description && ` · ${vote.description}`}
          </p>
        </header>
        <VoteResultChart stats={vote.stats.total} />
      </main>

      <footer class="vote-sharepic__footer">
        <div class="vote-sharepic__footer-text">
          Find out how individual MEPs, political groups, and countries voted:
          <br />
          <strong>HowTheyVote.eu/{vote.id}</strong>
        </div>
        <CCLogo />
      </footer>
    </div>
  );
}
