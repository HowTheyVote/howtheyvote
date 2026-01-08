import type { Vote } from "../api";
import { PUBLIC_URL } from "../config";
import { formatDate } from "../lib/dates";
import { Island } from "../lib/islands";
import { getSummaryFeedbackFormUrl } from "../lib/links";
import ShareButton from "./ShareButton";
import Stack from "./Stack";
import Wrapper from "./Wrapper";

import "./VoteHeader.css";

type VoteHeaderProps = {
  vote: Vote;
};

export default function VoteHeader({ vote }: VoteHeaderProps) {
  // Sometimes, vote titles contain non-breaking spaces. In many cases these
  // do not work well for large headings, especially on small screens
  const title = vote.display_title?.replace(/\u00A0/g, " ");

  return (
    <header className="vote-header">
      <Wrapper>
        <Stack space="sm">
          <h1 className="alpha">{title}</h1>
          <p>
            <strong>
              <time datetime={vote.timestamp}>
                {formatDate(vote.timestamp)}
              </time>
              {vote.reference && ` · ${vote.reference}`}
              {vote.description && ` · ${vote.description}`}
            </strong>
          </p>
          {vote.summary && (
            <>
              <div
                class="vote-header__summary"
                // biome-ignore lint/security/noDangerouslySetInnerHtml: Vote summary is trusted HTML
                dangerouslySetInnerHTML={{ __html: vote.summary.text }}
              />
              <p class="vote-header__feedback">
                <a
                  rel="noreferrer noopener"
                  target="_blank"
                  href={vote.summary.source_url}
                >
                  Read more
                </a>
                {"・"}
                <a
                  rel="noreferrer noopener"
                  target="_blank"
                  href={getSummaryFeedbackFormUrl(
                    vote.summary.source_type,
                    vote.id,
                  )}
                >
                  What do you think of this summary?
                </a>
              </p>
            </>
          )}
          <Island>
            <ShareButton
              title={vote.display_title}
              text={vote.display_title}
              url={new URL(`/votes/${vote.id}`, PUBLIC_URL)}
            />
          </Island>
        </Stack>
      </Wrapper>
    </header>
  );
}
