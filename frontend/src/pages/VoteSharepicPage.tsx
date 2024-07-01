import type { Request } from "@tinyhttp/app";
import { type Vote, getVote } from "../api";
import App from "../components/App";
import VoteSharepic from "../components/VoteSharepic";
import type { Loader, Page } from "../lib/server";

export const loader: Loader<Vote> = async (request: Request) => {
  const { data } = await getVote({ path: { vote_id: request.params.id } });
  return data;
};

export const VoteSharepicPage: Page<Vote> = ({ data }) => {
  return (
    <App title={[data.display_title, "Share picture"]}>
      <VoteSharepic vote={data} />
    </App>
  );
};
