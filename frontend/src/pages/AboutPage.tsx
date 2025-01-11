import { type Statistics, getStats } from "../api";
import App from "../components/App";
import BaseLayout from "../components/BaseLayout";
import Disclosure from "../components/Disclosure";
import Hero from "../components/Hero";
import Stack from "../components/Stack";
import Stats from "../components/Stats";
import StatsCard from "../components/StatsCard";
import Wrapper from "../components/Wrapper";
import { formatDate, formatNumber } from "../lib/dates";
import { getErrorReportFormUrl } from "../lib/links";
import type { Loader, Page } from "../lib/server";

export const loader: Loader<Statistics> = async () => {
  const { data } = await getStats();
  return data;
};

export const AboutPage: Page<Statistics> = ({ data }) => {
  return (
    <App title={"About"}>
      <BaseLayout>
        <Stack space="lg">
          <Hero
            title="About"
            text={
              "HowTheyVote.eu makes vote results of the European Parliament transparent and accessible – for citizens, journalists, researchers, and activists."
            }
          />
          <div class="px">
            <Wrapper>
              <Stack space="lg">
                <StatsSection stats={data} />

                <p>
                  The European Union is one of the largest democracies in the
                  world. The European Parliament, with its 720 members from the
                  EU’s 27 member states, represents just over 440 million
                  Europeans. Although the Parliament publishes information such
                  as agendas, minutes, and vote results on its website, it can
                  be quite difficult to find out what MEPs voted on or how a
                  particular vote turned out. HowTheyVote.eu compiles voting
                  data from various official sources and allows anyone to search
                  for votes and view the results.
                </p>

                <GeneralSection />
                <MethodologySection />
                <ReuseSection />
                <LicenseSection />
                <RelatedSection />
                <FundingSection />
                <ContactSection />
              </Stack>
            </Wrapper>
          </div>
        </Stack>
      </BaseLayout>
    </App>
  );
};

function StatsSection({ stats }: { stats: Statistics }) {
  const lastUpdate = new Date(stats.last_update_date);
  const today = new Date();
  const formattedLastUpdate =
    lastUpdate.toDateString() === today.toDateString()
      ? "Today"
      : formatDate(lastUpdate, "short");

  return (
    <Stats>
      <StatsCard value={formatNumber(stats.votes_total)} label="Votes" />
      <StatsCard value={formatNumber(stats.members_total)} label="MEPs" />
      <StatsCard value={formatNumber(stats.years_total)} label="Years" />
      <StatsCard value={formattedLastUpdate} label="Last updated" />
    </Stats>
  );
}

function GeneralSection() {
  return (
    <div>
      <h2 class="delta">General information</h2>
      <Disclosure title="I found incorrect data or a missing vote.">
        <p>
          Please use{" "}
          <a href={getErrorReportFormUrl()}>this form to report data errors</a>{" "}
          (such as missing votes or incorrect vote results). Thanks for your
          help! Your report helps us to improve the data quality on
          HowTheyVote.eu!
        </p>
      </Disclosure>
      <Disclosure title="How often is the data on HowTheyVote.eu updated?">
        <p>
          HowTheyVote.eu collects data in an automated way. During a plenary
          sessions we fetch the latest vote results multiple times per day.
          Usually, vote results are available on HowTheyVote.eu within 30
          minutes after they have been published by the European Parliament.
        </p>
      </Disclosure>
      <Disclosure title="I am looking for a specific vote. Why can't I find it on HowTheyVote.eu?">
        <p>
          Currently, only roll-call votes can be found on HowTeyVote.eu. Other
          types of votes, such as secret votes or simple votes by show of hands
          cannot be found. If you think a roll-call vote is missing, please
          report it <a href={getErrorReportFormUrl()}>using this form</a>.
        </p>
      </Disclosure>
      <Disclosure title="What is a roll-call vote?">
        <p>
          In case of a roll-call vote the individual votes cast by each MEP are
          recorded and published as part of the plenary minutes. However, not
          every vote in the European Parliament is a roll-call vote. Only when
          requested by a certain threshold of MEPs a roll-call vote is taken.
        </p>
      </Disclosure>
      <Disclosure title="What do the different values for the voting behavior mean?">
        <p>
          There are four possible values for the voting behavior of an MEP:
          "For", "Against", "Abstention", and "Did not vote". "Did not vote"
          means that the MEP did not participate in the vote, for example
          because the MEP was not present while the vote took place. "For",
          "Against", and "Abstention" are options that the MEP actively chose at
          the time of the vote.
        </p>
      </Disclosure>
      <Disclosure title="Where can I find the results of non-roll-call votes?">
        <p>
          HowTheyVote.eu currently does not provide data about non-roll-call
          votes. However, you can refer to the official vote results published
          on the{" "}
          <a href="https://www.europarl.europa.eu/plenary/en/votes.html?tab=votes">
            European Parliament website
          </a>
          .
        </p>
      </Disclosure>
      <Disclosure title="Where can I find the results of committee votes?">
        <p>
          HowTheyVote.eu currently does not provide data about votes in
          committees. You can find committee vote results{" "}
          <a href="https://www.europarl.europa.eu/committees/en/home">
            on the website of the respective committee
          </a>
          .
        </p>
      </Disclosure>
      <Disclosure title="Where can I find the results of votes on amendments?">
        <p>
          While HowTheyVote.eu collects the results of votes on amendments, this
          data is currently not displayed on our website. We plan to implement
          this feature in the future. In the meantime, you can find the results
          of votes on amendments on the{" "}
          <a href="https://www.europarl.europa.eu/plenary/en/votes.html?tab=votes">
            European Parliament website
          </a>
          .
        </p>
      </Disclosure>
      <Disclosure title="Where does the European Parliament publish official vote results?">
        <p>
          The European Parliament publishes vote results for roll-call and
          non-roll-call vote results{" "}
          <a href="https://www.europarl.europa.eu/plenary/en/votes.html?tab=votes">
            on its website
          </a>
          . The European Parliament also publishes a growing number of datasets,
          including vote results, in machine-readble formats in the{" "}
          <a href="https://data.europarl.europa.eu/en/home">
            European Parliament Open Data Portal
          </a>
          .
        </p>
      </Disclosure>
      <Disclosure title="Where can I find vote results for previous terms/years?">
        HowTheyVote.eu currently provides vote results starting with the 9th
        term of the European Parliament. You can download vote results for
        previous terms from{" "}
        <a href="https://www.europarl.europa.eu/plenary/en/votes.html?tab=votes">
          the official website of the European Parliament
        </a>
        . You may also be interested in the{" "}
        <a href="https://cadmus.eui.eu/handle/1814/74918">VoteWatch dataset</a>{" "}
        which contains enriched roll-call vote results from July 2004 up to June
        2022.
      </Disclosure>
      <Disclosure title="Where can I find vote corrections?">
        After a roll-call vote, MEPs can submit a correction of their vote. The
        corrected vote is published in the plenary minutes. However, vote
        corrections do not change the result of the vote. As such, we currently
        do not collect or display information about vote corrections.
      </Disclosure>
    </div>
  );
}

function MethodologySection() {
  return (
    <div>
      <h2 class="delta">Methodology</h2>
      <Disclosure title="What is the source for the data on HowTheyVote.eu?">
        <p>
          HowTheyVote.eu compiles voting data from multiple official sources,
          including the{" "}
          <a href="https://www.europarl.europa.eu/plenary/en/votes.html?tab=votes">
            roll-call vote results
          </a>{" "}
          published as part of the plenary minutes, data about legislative
          procedures from the{" "}
          <a href="https://oeil.secure.europarl.europa.eu/oeil/home/home.do">
            Legislative Observatory
          </a>
          , and{" "}
          <a href="https://www.europarl.europa.eu/news/en">press releases</a>{" "}
          published by the European Parliament. You can find a list of sources
          for each vote on the vote detail pages on HowTheyVote.eu.
        </p>
      </Disclosure>
      <Disclosure title="Is the data on HowTheyVote.eu complete?">
        <Stack space="xxs">
          <p>
            HowTheyVote.eu currently only collects data about roll-call votes.
            We currently do not provide data about other votes. All data for
            HowTheyVote.eu is collected and processed in a fully automated way.
            While we aim to provide complete and correct data, we cannot rule
            out the possibility that individual votes are missing or contain
            errors. If you think there’s missing data on HowTheyVote.eu or have
            found an error,{" "}
            <a href={getErrorReportFormUrl()}>please contact us</a>.
          </p>
        </Stack>
      </Disclosure>
      <Disclosure title="What is a featured vote?">
        <p>
          HowTheyVote.eu marks a vote as featured when we have found a press
          release about the vote published by the European Parliament. However,
          we are not always able to reliably link press releases to votes. In
          the future, we may use additional indicators for featured votes.
        </p>
      </Disclosure>
    </div>
  );
}

function ReuseSection() {
  return (
    <div>
      <h2 class="delta">Reusing the data</h2>
      <Disclosure title="I’m a journalist, researcher, or activist. Can I use your data?">
        <p>
          Yes! We provide access to the HowTheyVote.eu data under an open
          license. If you use data published by HowTheyVote.eu please make sure
          you’ve read the <a href="#license">license terms</a> and provide
          proper attribution. If you publish your work, we'd appreciate if you
          could share a copy or link with us! We are always curious to see how
          others use voting data.
        </p>
      </Disclosure>
      <Disclosure title="How should I cite HowTheyVote.eu?">
        <p>
          You can cite HowTheyVote.eu in the same way you would cite any other
          online resource or dataset. If you use data published by
          HowTheyVote.eu please make sure you’ve read the{" "}
          <a href="#license">license terms</a> and provide proper attribution.
        </p>
      </Disclosure>
      <Disclosure title="How can I download the data?">
        <p>
          We currently provide multiple different ways to download data from
          HowTheyVote.eu. Data for individual votes can be downloaded in JSON
          and CSV formats using the links on vote pages on HowTheyVote.eu. We
          also provide an <a href="/developers">experimental API</a>. A
          regularly updated export of our dataset can also be found on{" "}
          <a href="https://github.com/howTheyVote/data">GitHub</a>.
        </p>
      </Disclosure>
      <Disclosure title="Can I download all available data at once?">
        <p>
          Yes, we publish a weekly updated export of our dataset and
          documentation of the data schema on{" "}
          <a href="https://github.com/howTheyVote/data">GitHub</a>. If you have
          any feedback or questions, please contact us using the email address
          below.
        </p>
      </Disclosure>
    </div>
  );
}

function LicenseSection() {
  return (
    <div class="prose" id="license">
      <h3 class="delta">License</h3>
      <p>
        The voting data made available via downloads and the HowTheyVote.eu API
        is made available under the{" "}
        <a href="http://opendatacommons.org/licenses/odbl/1.0/">
          Open Database License
        </a>
        . Any rights in individual contents of the database are licensed under
        the{" "}
        <a href="http://opendatacommons.org/licenses/dbcl/1.0/">
          Database Contents License
        </a>
        , unless otherwise noted.
      </p>
      <p>
        In particular, photos (including thumbnails) of MEPs and vote summaries
        are <strong>not</strong> covered by the Database Contents License. These
        contents are sourced from the official website of the European
        Parliament. Please refer to the respective{" "}
        <a href="https://www.europarl.europa.eu/legal-notice/en/">
          copyright notice
        </a>
        .
      </p>
    </div>
  );
}

function RelatedSection() {
  return (
    <div class="prose">
      <h3 class="delta">Related work</h3>
      <ul>
        <li>
          <a href="https://parltrack.eu">Parltrack</a> is an open source project
          that improves access to information about legislative processes,
          including (but not limited to) vote results of the European
          Parliament.
        </li>
        <li>
          <a href="https://www.abgeordnetenwatch.de/eu/abstimmungen">
            abgeordnetenwatch.eu
          </a>{" "}
          is a German NGO that allows citizen to publicly ask questions elected
          representatives in the federal and state parliaments as well as the
          European Parliament questions. abgeordnetenwatch.eu also publishes
          voting records of German MEPs for selected votes.
        </li>
        <li>
          The{" "}
          <a href="https://data.europarl.europa.eu/en/home">
            European Parliament Open Data Portal
          </a>{" "}
          provides access to a growing collection of machine-readable datasets,
          including vote results.
        </li>
        <li>
          <a href="https://votewatch.eu/">VoteWatch Europe</a> was an NGO that
          maintained a database of vote results. VoteWatch shut down operations
          in 2022, but the{" "}
          <a href="https://cadmus.eui.eu/handle/1814/74918">
            VoteWatch dataset
          </a>{" "}
          covering votes between July 2004 up to June 2022 has been published.
        </li>
      </ul>
    </div>
  );
}

function FundingSection() {
  return (
    <div class="prose">
      <h3 class="delta">Funding and sponsors</h3>
      <p>
        A first version of HowTheyVote.eu has been funded by the German Federal
        Ministry of Research and Education as part of the 9th round of the{" "}
        <a href="https://prototypefund.de/">Prototype Fund</a> under the funding
        reference 1IS21818.
      </p>
      <p>
        <a href="https://tuta.com">Tuta</a> supports HowTheyVote.eu with a
        secure and ad-free email account.
      </p>
    </div>
  );
}

function ContactSection() {
  return (
    <div class="prose">
      <h3 class="delta">Contact</h3>
      <p>You can contact us via email at mail [at] howtheyvote.eu.</p>
    </div>
  );
}
