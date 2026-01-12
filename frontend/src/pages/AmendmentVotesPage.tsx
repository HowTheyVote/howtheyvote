import { getVote, type Vote } from "../api";
import AmendmentHeader from "../components/AmendmentHeader";
import AmendmentVoteCard from "../components/AmendmentVoteCard";
import App from "../components/App";
import BaseLayout from "../components/BaseLayout";
import Callout from "../components/Callout";
import Stack from "../components/Stack";
import VoteCards from "../components/VoteCards";
import Wrapper from "../components/Wrapper";
import { HTTPException } from "../lib/http";
import type { Loader, Page, Request } from "../lib/server";

export const loader: Loader<Vote> = async (request: Request) => {
  const { data } = await getVote({ path: { vote_id: request.params.id } });

  // `/amendments` opened on non-main vote which cannot have amendments
  if (!data.is_main) throw new HTTPException(404);

  data.related = data.related.filter(
    (related_vote) => !related_vote.is_main || related_vote.id === data.id,
  );

  // `/amendments` opened on a main vote which does not have amendments
  if (data.related.length <= 1) throw new HTTPException(404);

  return data;
};

export const AmendmentVotesPage: Page<Vote> = ({ data }) => {
  return (
    <App title={[data.display_title, "Amendments"]}>
      <BaseLayout>
        <Stack space="lg">
          <div>
            <AmendmentHeader vote={data} />
            <Callout>
              <p>
                Before voting on a text, MEPs might propose changes or vote on
                individual parts of the text. These votes take place before the
                final vote. View the result of the{" "}
                <a href={`/votes/${data.id}`}>final vote</a>.
              </p>
            </Callout>
          </div>
          <div class="px">
            <Wrapper>
              <VoteCards votes={data.related}>
                {({ vote }: { vote: (typeof data.related)[number] }) => (
                  <AmendmentVoteCard vote={vote} />
                )}
              </VoteCards>
            </Wrapper>
          </div>
        </Stack>
      </BaseLayout>
    </App>
  );
};
