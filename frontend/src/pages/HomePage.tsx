import { getSessions, type PlenarySession } from "../api";
import App from "../components/App";
import BaseLayout from "../components/BaseLayout";
import Footer from "../components/Footer";
import Header from "../components/Header";
import SearchForm from "../components/SearchForm";
import { formatDate } from "../lib/dates";
import type { Loader, Page } from "../lib/server";

import "./HomePage.css";

const LOCATION_NAMES: Record<
  NonNullable<PlenarySession["location"]>,
  string
> = {
  BRU: "Brussels",
  SXB: "Strasbourg",
};

type HomePageData = {
  currentSession?: PlenarySession;
  lastSession?: PlenarySession;
};

export const loader: Loader<HomePageData> = async () => {
  const { data: current } = await getSessions({
    query: {
      status: "current",
      page_size: 1,
      sort_order: "asc",
    },
  });

  const { data: past } = await getSessions({
    query: {
      status: "past",
      page_size: 1,
      sort_order: "desc",
    },
  });

  return {
    currentSession: current.results[0],
    lastSession: past.results[0],
  };
};

export const HomePage: Page<HomePageData> = ({ data }) => {
  const { currentSession, lastSession } = data;

  const header = <Header style="dark" />;
  const footer = (
    <Footer
      style="dark"
      copyright={
        <>
          {"Background: © European Union 2019 · "}
          <a
            rel="noopener noreferrer"
            href="https://multimedia.europarl.europa.eu/en/stockshot-of-hemicycle-of-european-parliament-in-strasbourg-vote-by-show-of-hand_20191023_EP-094585E_FMA_047_p"
          >
            Source: EP
          </a>
        </>
      }
    />
  );

  return (
    <App title={"European Parliament vote results"} head={<MetaTags />}>
      <BaseLayout header={header} footer={footer} style="dark">
        <div class="home-page">
          <div class="home-page__wrapper">
            <h1 class="home-page__title">
              Find out how Members of the European Parliament vote.
            </h1>

            <SearchForm style="dark" />

            <div class="home-page__hint">
              Try <a href="/votes?q=Ukraine">Ukraine</a>,{" "}
              <a href="/votes?q=Frontex">Frontex</a>, or{" "}
              <a href="/votes?q=Environment">Environment</a>.
            </div>

            <aside class="home-page__session-info">
              <SessionInfo
                currentSession={currentSession}
                lastSession={lastSession}
              />
            </aside>
          </div>
        </div>
      </BaseLayout>
    </App>
  );
};

type SessionInfoProps = {
  currentSession?: PlenarySession;
  lastSession?: PlenarySession;
};

function SessionInfo({ currentSession, lastSession }: SessionInfoProps) {
  if (currentSession) {
    const locationName =
      currentSession.location && LOCATION_NAMES[currentSession.location];

    return (
      <>
        Parliament is meeting {locationName && `in ${locationName} `}
        this week. <br />
        <strong>
          <a href="/votes">View vote results</a>
        </strong>{" "}
        as they become available.
      </>
    );
  }

  if (lastSession) {
    const locationName =
      lastSession.location && LOCATION_NAMES[lastSession.location];

    // Format dates
    const startDate = formatDate(new Date(lastSession.start_date), "short");
    const endDate = formatDate(new Date(lastSession.end_date), "short");

    return (
      <>
        The last plenary session was held{" "}
        {locationName && `in ${locationName} `}
        from {startDate?.replaceAll(" ", "\u00a0")} to{" "}
        {endDate?.replace(" ", "\u00a0")}.{" "}
        <strong>
          <a href="/votes">View vote results</a>
        </strong>{" "}
        from this session.
      </>
    );
  }

  return null;
}

function MetaTags() {
  return (
    <>
      <meta
        name="description"
        content="Find out how Members of the European Parliament vote."
      />
      <meta property="og:type" content="website" />
      <meta property="og:site_name" content="HowTheyVote.eu" />
      <meta
        property="og:title"
        content="Find out how Members of the European Parliament vote"
      />
      <meta property="og:image" content="/static/sharepic-default.png" />
      <meta
        property="og:image:alt"
        content="A photo of the hemicycle in the European Parliament building in Strasbourg, with text overlay: “HowTheyVote.eu. Find out how the Members of the European Parliament vote.”"
      />
    </>
  );
}
