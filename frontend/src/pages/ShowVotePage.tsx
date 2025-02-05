import { type Vote, getVote } from "../api";
import App from "../components/App";
import BaseLayout from "../components/BaseLayout";
import Footer from "../components/Footer";
import Sources from "../components/Sources";
import Stack from "../components/Stack";
import VoteHeader from "../components/VoteHeader";
import VoteResultChart from "../components/VoteResultChart";
import VoteTabs from "../components/VoteTabs";
import Wrapper from "../components/Wrapper";
import { formatDate } from "../lib/dates";
import { Island } from "../lib/islands";
import { getDownloadUrl, getErrorReportFormUrl } from "../lib/links";
import { getLogger } from "../lib/logging";
import { serializeMemberVotes } from "../lib/serialization";
import type { Request } from "../lib/server";
import type { Loader, Page } from "../lib/server";

const log = getLogger();

export const loader: Loader<Vote> = async (request: Request) => {
  const { data } = await getVote({ path: { vote_id: request.params.id } });

  if (!request.isBot) {
    log.info({ msg: "Handling vote request", vote_id: data.id });
  }

  return data;
};

export const ShowVotePage: Page<Vote> = ({ data }) => {
  const footer = <Footer copyright={<Copyright vote={data} />} />;
  const errorReportFormUrl = getErrorReportFormUrl("INCORRECT_RESULT", {
    voteId: data.id,
  });
  const csvUrl = getDownloadUrl(data.id, "csv");
  const jsonUrl = getDownloadUrl(data.id, "json");

  return (
    <App
      title={[data.display_title, "Vote Results"]}
      head={<MetaTags vote={data} />}
    >
      <BaseLayout footer={footer}>
        <Stack space="lg">
          <VoteHeader vote={data} />
          <div className="px">
            <Wrapper>
              {data.stats && <VoteResultChart stats={data.stats.total} />}
            </Wrapper>
          </div>
          <div className="px">
            <Wrapper>
              {data.member_votes && data.stats && (
                <Island>
                  <VoteTabs
                    memberVotes={serializeMemberVotes(data.member_votes)}
                    groupStats={data.stats.by_group}
                    countryStats={data.stats.by_country}
                  />
                </Island>
              )}
            </Wrapper>
          </div>
          <div class="px">
            <Wrapper>
              <h2 class="delta mb--xs">Open Data</h2>
              <p>
                We provide raw voting data for this vote that you can use for
                data analysis, visualizations, or research. Read more about{" "}
                <a href="/about#license">our data license</a> or download data
                in <a href={csvUrl}>CSV format</a> or{" "}
                <a href={jsonUrl}>JSON format</a>.
              </p>
            </Wrapper>
          </div>
          <div class="px">
            <Wrapper>
              <h2 class="delta mb--xs">Sources</h2>
              <p class="mb--xs">
                HowTheyVote.eu compiles information from multiple official
                sources. The information on this page is based on the following
                sources:
              </p>
              {data.sources && <Sources sources={data.sources} />}
            </Wrapper>
          </div>
          <div class="px">
            <Wrapper>
              <h2 class="delta mb--xs">Report an error</h2>
              <p>
                If you think the data displayed on this page is incorrect you
                can{" "}
                <a href={errorReportFormUrl}>
                  report a data error using this form
                </a>
                . Thanks for your help! Your report helps us to improve the data
                quality on HowTheyVote.eu.
              </p>
            </Wrapper>
          </div>
        </Stack>
      </BaseLayout>
    </App>
  );
};

function Copyright({ vote }: { vote: Vote }) {
  let copyright = (
    <>
      {"MEP photos: © European Union 2019 · "}
      <a
        rel="noopener noreferrer"
        href="https://www.europarl.europa.eu/meps/en/directory/9"
      >
        Source: EP
      </a>
    </>
  );

  if (vote.facts) {
    copyright = (
      <>
        {copyright}
        <br />
        {"Summary: © European Union "}
        {new Date(vote.timestamp).getFullYear()}
        {" · "}
        <a
          rel="noopener noreferrer"
          href="https://www.europarl.europa.eu/news/en"
        >
          Source: EP
        </a>
      </>
    );
  }

  return copyright;
}

function MetaTags({ vote }: { vote: Vote }) {
  if (!vote.sharepic_url) {
    return null;
  }

  const date = formatDate(vote.timestamp);
  const stats = vote.stats.total;
  const total = stats.FOR + stats.AGAINST + stats.ABSTENTION;

  const altText = `A barchart visualizing the result of a European Parliament vote. The vote took place on ${date}, and is titled “${vote.display_title}”. The chart has three bars representing the ${stats.FOR} MEPs who voted in favor, the ${stats.AGAINST} MEPs who voted against, and the ${stats.ABSTENTION} MEPs who abstained. A total of ${total} MEPs participated in the vote and ${stats.DID_NOT_VOTE} did not vote.`;
  const title = `Vote results: ${vote.display_title}`;
  const description =
    "Find out how the Members of the European Parliament voted.";

  return (
    <>
      <meta name="description" content={description} />
      <meta property="og:site_name" content="HowTheyVote.eu" />
      <meta property="og:type" content="article" />
      <meta property="og:title" content={title} />
      <meta property="og:description" content={description} />
      <meta property="og:image" content={vote.sharepic_url} />
      <meta property="og:image:alt" content={altText} />
      <meta property="article:published_time" content={vote.timestamp} />
    </>
  );
}
