import { getVote, type Vote } from "../api";
import AmendmentVoteCards from "../components/AmendmentVoteCards";
import App from "../components/App";
import BaseLayout from "../components/BaseLayout";
import Callout from "../components/Callout";
import Stack from "../components/Stack";
import VoteHeader from "../components/VoteHeader";
import Wrapper from "../components/Wrapper";
import type { Loader, Page, Request } from "../lib/server";

export const loader: Loader<Vote> = async (request: Request) => {
  const { data } = await getVote({ path: { vote_id: request.params.id } });

  // The last element of `related` is the vote itself
  if (data.related[data.related.length - 1].id === Number(request.params.id))
    data.related = data.related.slice(0, -1);

  return data;
};

export const ShowAmendmentVotesPage: Page<Vote> = ({ data }) => {
  return (
    <App title={[data.display_title, "Amendments"]}>
      <BaseLayout>
        <Stack space="lg">
          <VoteHeader vote={data} />
          <Wrapper>
            <Callout title="Hello">
              <p>
                The votes are <b>amendments</b>. Amendments change the final
                text that parliament votes on, but do not produce Parliament
                decisions on their own. You can see the result of the final vote{" "}
                <a href={`/votes/${data.id}`}>here</a>
              </p>
            </Callout>
            <div className="px">
              <AmendmentVoteCards votes={data.related} />
            </div>
          </Wrapper>
        </Stack>
      </BaseLayout>
    </App>
  );
};
