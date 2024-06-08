import type { Request } from "@tinyhttp/app";
import { type Vote, api } from "../api";
import App from "../components/App";
import VoteSharepic from "../components/VoteSharepic";
import type { Loader, Page } from "../lib/server";

export const loader: Loader<Vote> = async (request: Request) => {
  return await api.votes.getVote({ voteId: request.params.id });
};

export const VoteSharepicPage: Page<Vote> = ({ data }) => {
  return (
    <App title={[data.display_title, "Share picture"]}>
      <VoteSharepic vote={data} />
    </App>
  );
};
