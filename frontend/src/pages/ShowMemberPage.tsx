import type { Request } from "@tinyhttp/app";
import {
  getMember,
  getMemberVotes,
  type Member,
  type MemberVotesQueryResponse,
} from "../api";
import App from "../components/App";
import BaseLayout from "../components/BaseLayout";
import Footer from "../components/Footer";
import MemberHeader from "../components/MemberHeader";
import SearchForm from "../components/SearchForm";
import SearchResults from "../components/SearchResults";
import Stack from "../components/Stack";
import Wrapper from "../components/Wrapper";
import { PUBLIC_URL } from "../config";
import { FACETS, SearchQuery, SORT_PARAMS } from "../lib/search";
import type { Loader, Page } from "../lib/server";

type ShowMemberPageData = {
  member: Member;
  votes: MemberVotesQueryResponse;
};

export const loader: Loader<ShowMemberPageData> = async (request: Request) => {
  const searchQuery = SearchQuery.fromUrl(new URL(request.url, PUBLIC_URL));

  const { data: member } = await getMember({
    path: { member_id: request.params.id },
  });

  const { data: votes } = await getMemberVotes({
    path: {
      member_id: request.params.id,
    },
    query: {
      q: searchQuery.q,
      page: searchQuery.page,
      facets: [...FACETS],
      ...searchQuery.filters,
      ...SORT_PARAMS[searchQuery.sort],
    },
  });

  return { member, votes };
};

export const ShowMemberPage: Page<ShowMemberPageData> = ({ data, request }) => {
  const url = new URL(request.url, PUBLIC_URL);
  const searchQuery = SearchQuery.fromUrl(url);

  const copyright = (
    <>
      {`MEP photos: © European Union 2019-${new Date().getFullYear()} · `}
      <a
        rel="noopener noreferrer"
        href="https://www.europarl.europa.eu/meps/en/directory"
      >
        Source: EP
      </a>
    </>
  );

  const footer = <Footer copyright={copyright} />;

  return (
    <App
      title={[
        `${data.member.first_name} ${data.member.last_name}`,
        "Member of the European Parliament",
        "Votes",
      ]}
    >
      <BaseLayout footer={footer}>
        <Stack>
          <MemberHeader
            member={data.member}
            size={searchQuery.page === 1 ? "lg" : undefined}
          />
          <div class="px">
            <Wrapper>
              <Stack space="xxs">
                <SearchForm action={searchQuery.base} value={searchQuery.q} />
                <SearchResults data={data.votes} url={url} thumb="position" />
              </Stack>
            </Wrapper>
          </div>
        </Stack>
      </BaseLayout>
    </App>
  );
};
