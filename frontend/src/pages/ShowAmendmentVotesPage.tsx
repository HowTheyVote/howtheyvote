import { getVote, type Vote } from "../api";
import AmendmentHeader from "../components/AmendmentHeader";
import AmendmentVoteCards from "../components/AmendmentVoteCards";
import App from "../components/App";
import BaseLayout from "../components/BaseLayout";
import Callout from "../components/Callout";
import Stack from "../components/Stack";
import Wrapper from "../components/Wrapper";
import type { Loader, Page, Request } from "../lib/server";

export const loader: Loader<Vote> = async (request: Request) => {
  const { data } = await getVote({ path: { vote_id: request.params.id } });
  // The last element of `related` is the vote itself
  if (data.related[data.related.length - 1].id === request.params.id)
    data.related = data.related.slice(0, -1);

  return data;
};

export const ShowAmendmentVotesPage: Page<Vote> = ({ data }) => {
  return (
    <App title={[data.display_title, "Amendments"]}>
      <BaseLayout>
        <Stack space="lg">
          <AmendmentHeader vote={data} />
          <Wrapper>
            <Callout>
              <p>
                The votes on this page were on <b>amendments</b>.<br />
                Amendments aim at changing the text of reports. The outcome of
                amendments do not dictate the outcome of the vote on a report.
                <br /> Successful amendments do not become part of official
                Parliament positions if the report is not accepted in its{" "}
                <a href={`/votes/${data.id}`}>final vote</a>.
              </p>
            </Callout>
          </Wrapper>
          <Wrapper>
            <div className="px">
              <AmendmentVoteCards votes={data.related} />
            </div>
          </Wrapper>
        </Stack>
      </BaseLayout>
    </App>
  );
};
