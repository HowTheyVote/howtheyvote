import type { Request } from "@tinyhttp/app";
import { getMember, type Member } from "../api";
import App from "../components/App";
import MemberSharepic from "../components/MemberSharepic";
import type { Loader, Page } from "../lib/server";

export const loader: Loader<Member> = async (request: Request) => {
  const { data } = await getMember({ path: { member_id: request.params.id } });
  return data;
};

export const MemberSharepicPage: Page<Member> = ({ data }) => {
  return (
    <App title={[`${data.first_name} ${data.last_name}`, "Share picture"]}>
      <MemberSharepic member={data} />
    </App>
  );
};
