import { getVote, type Vote } from "../api";
import App from "../components/App";
import BaseLayout from "../components/BaseLayout";
import Callout from "../components/Callout";
import CopyrightLink from "../components/CopyrightLink";
import DatawrapperLink from "../components/DatawrapperLink";
import ExternalLinks from "../components/ExternalLinks";
import Footer from "../components/Footer";
import PageNav from "../components/PageNav";
import PageNavItem from "../components/PageNavItem";
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
import type { Loader, Page, Request } from "../lib/server";

const log = getLogger();

export const loader: Loader<Vote> = async (request: Request) => {
  const { data } = await getVote({ path: { vote_id: request.params.id } });

  if (!request.isBot) {
    log.info({ msg: "Handling vote request", vote_id: data.id });
  }

  return data;
};

export const VotePage: Page<Vote> = ({ data }) => {
  const footer = <Footer copyright={<Copyright vote={data} />} />;
  const errorReportFormUrl = getErrorReportFormUrl("INCORRECT_RESULT", {
    voteId: data.id,
  });
  const csvUrl = getDownloadUrl(data.id, "csv");
  const jsonUrl = getDownloadUrl(data.id, "json");

  const hasAmendments =
    data.is_main &&
    data.related.filter(
      (related_vote) => !related_vote.is_main || related_vote.id === data.id,
    ).length > 1;

  // This will not work in all cases, but might be good enough in combination with the amendment condition above.
  const main_vote = data.related.find((related_vote) => related_vote.is_main);

  return (
    <App
      title={[data.display_title, "Vote Results"]}
      head={<MetaTags vote={data} />}
    >
      <BaseLayout footer={footer}>
        <VoteHeader vote={data} />
        <PageNav>
          <PageNavItem href="#result">Vote result</PageNavItem>
          {hasAmendments && (
            <PageNavItem href="#amendments">Amendments</PageNavItem>
          )}
          <PageNavItem href="#more-information">More information</PageNavItem>
          <PageNavItem href="#open-data">Open data</PageNavItem>
          <PageNavItem href="#embed">Embed</PageNavItem>
          <PageNavItem href="#sources">Sources</PageNavItem>
          <PageNavItem href="#errors">Report an error</PageNavItem>
        </PageNav>
        <Stack space="lg">
          <div id="result" className="px mt--lg">
            <Wrapper>
              <Stack space="sm">
                {!data.is_main && (
                  <Callout>
                    <p>
                      This is a vote on an amendment! View the result of the{" "}
                      <a href={`/votes/${main_vote?.id}`}>final vote</a>.
                    </p>
                  </Callout>
                )}

                {data.stats && <VoteResultChart stats={data.stats.total} />}
              </Stack>
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
          {hasAmendments && (
            <div class="px">
              <Wrapper>
                <h2 id="amendments" class="delta mb--xs">
                  Amendments
                </h2>
                <p class="mb--xs">
                  There have been votes on amendments.{" "}
                  <a href={`/votes/${data.id}/amendments`}>
                    View all roll-call votes,
                  </a>{" "}
                  including amendments.
                </p>
              </Wrapper>
            </div>
          )}
          {data.links.length > 0 && (
            <div class="px">
              <Wrapper>
                <h2 id="more-information" class="delta mb--xs">
                  More information
                </h2>
                <p class="mb--xs">
                  The following external links provide additional information
                  about this vote. All links point to official websites of the
                  European Parliament.
                </p>
                <ExternalLinks links={data.links} />
              </Wrapper>
            </div>
          )}
          <div class="px">
            <Wrapper>
              <h2 id="open-data" class="delta mb--xs">
                Open data
              </h2>
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
              <h2 id="embed" class="delta mb--xs">
                Embed
              </h2>
              <p>
                Want to embed the results of this vote on your website? Use our{" "}
                <Island>
                  <DatawrapperLink
                    voteId={data.id}
                    title={data.display_title || data.id.toString()}
                    timestamp={data.timestamp}
                    reference={data.reference}
                    description={data.description}
                    stats={data.stats.total}
                  >
                    Datawrapper template
                  </DatawrapperLink>
                </Island>{" "}
                to create an interactive table in just a few clicks.
              </p>
            </Wrapper>
          </div>
          <div class="px">
            <Wrapper>
              <h2 id="sources" class="delta mb--xs">
                Sources
              </h2>
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
              <h2 id="errors" class="delta mb--xs">
                Report an error
              </h2>
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
    <CopyrightLink
      content="MEP photos"
      sourceUrl="https://www.europarl.europa.eu/meps/en/directory"
      startYear={2019}
      endYear={new Date().getFullYear()}
    />
  );

  if (vote.summary) {
    copyright = (
      <>
        {copyright}
        <br />
        <CopyrightLink
          content="Summary"
          sourceUrl={vote.summary.source_url}
          year={new Date(vote.timestamp).getFullYear()}
        />
      </>
    );
  }

  return copyright;
}

function MetaTags({ vote }: { vote: Vote }) {
  const date = formatDate(vote.timestamp);
  const stats = vote.stats.total;
  const total = stats.FOR + stats.AGAINST + stats.ABSTENTION;

  const altText = `A barchart visualizing the result of a European Parliament vote. The vote took place on ${date}, and is titled “${vote.display_title}”. The chart has three bars representing the ${stats.FOR} MEPs who voted in favor, the ${stats.AGAINST} MEPs who voted against, and the ${stats.ABSTENTION} MEPs who abstained. A total of ${total} MEPs participated in the vote and ${stats.DID_NOT_VOTE} did not vote.`;
  const title = `Vote results: ${vote.display_title}`;
  const description =
    "Find out how the Members of the European Parliament voted.";

  return (
    <>
      {!vote.is_main && <meta name="robots" content="noindex" />}
      {vote.sharepic_url && (
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
      )}
    </>
  );
}
