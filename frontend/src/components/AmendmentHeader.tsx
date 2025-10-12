import type { Vote } from "../api";
import { formatDate } from "../lib/dates";
import Stack from "./Stack";
import Wrapper from "./Wrapper";
import "./VoteHeader.css";

type VoteHeaderProps = {
  vote: Vote;
};

export default function AmendmentHeader({ vote }: VoteHeaderProps) {
  // Sometimes, vote titles contain non-breaking spaces. In many cases these
  // do not work well for large headings, especially on small screens
  const title = vote.display_title?.replace(/\u00A0/g, " ");

  return (
    <header className="vote-header">
      <Wrapper>
        <Stack space="sm">
          <h1>
            <div class="beta">
              Amendments<span class="visually-hidden">:</span>
            </div>
            <div class="alpha">{title}</div>
          </h1>
          <p>
            <strong>
              <time datetime={vote.timestamp}>
                {formatDate(vote.timestamp)}
              </time>
              {vote.reference && ` · ${vote.reference}`}
            </strong>
          </p>
        </Stack>
      </Wrapper>
    </header>
  );
}
