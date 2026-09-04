import App from "../components/App";
import BaseLayout from "../components/BaseLayout";
import DataProducts from "../components/DataProducts";
import Hero from "../components/Hero";
import PageNav from "../components/PageNav";
import PageNavItem from "../components/PageNavItem";
import Showcase from "../components/Showcase";
import Stack from "../components/Stack";
import Wrapper from "../components/Wrapper";
import type { Page } from "../lib/server";

export const OpenDataPage: Page = () => {
  return (
    <App title={"Open Data"}>
      <BaseLayout>
        <Stack space="lg">
          <div>
            <Hero
              title="Open Data"
              text="We believe it should be easy to work with European Parliament voting data. That’s why we publish our data under an open license."
            />
            <PageNav>
              <PageNavItem href="#products">Data</PageNavItem>
              <PageNavItem href="#license">License</PageNavItem>
              <PageNavItem href="#tutorials">Tutorials</PageNavItem>
              <PageNavItem href="#showcase">Showcase</PageNavItem>
              <PageNavItem href="#faq">FAQ</PageNavItem>
            </PageNav>
          </div>
          <div class="px">
            <Wrapper>
              <Stack space="xl">
                <Stack>
                  <Stack space="xs">
                    <h2 id="data" class="delta">
                      Data
                    </h2>
                    <p>
                      We make our data avaialble in multiple ways to suit
                      different use cases – whether you want to conduct a
                      large-scale data analysis or are interested in the results
                      of individual votes.
                    </p>
                  </Stack>
                  <DataProducts />
                </Stack>

                <Stack space="xs">
                  <h2 id="license" class="delta">
                    License
                  </h2>

                  <div class="prose">
                    <p>
                      We make our data available under the{" "}
                      <a href="http://opendatacommons.org/licenses/odbl/1.0/">
                        Open Database License (ODbL)
                      </a>
                      . Any rights in individual contents of the database are
                      licensed under the{" "}
                      <a href="http://opendatacommons.org/licenses/dbcl/1.0/">
                        Database Contents License
                      </a>
                      , unless otherwise noted.
                    </p>
                    <p>
                      Photos of MEPs and vote summaries are <strong>not</strong>{" "}
                      covered by the Database Contents License. These contents
                      are sourced from the official website of the European
                      Parliament. Please refer to the respective{" "}
                      <a href="https://www.europarl.europa.eu/legal-notice/en/">
                        copyright notice
                      </a>
                      .
                    </p>

                    <p>
                      Under the Open Database License, you are free to use,
                      modify, and build upon the data from HowTheyVote.eu as
                      long as you comply with the license conditions. In
                      particular, you must:
                    </p>
                    <p>
                      <strong>Provide attribution:</strong> You must include a
                      link to HowTheyVote.eu as the source and make clear the
                      license, so that others are aware that they can also
                      freely use the data. For example:
                    </p>
                    <blockquote>
                      Data source:{" "}
                      <a href="https://howtheyvote.eu">
                        HowTheyVote.eu (Open Database License)
                      </a>
                    </blockquote>
                    <p>
                      <strong>Share under the same license:</strong> When you
                      make available data from HowTheyVote.eu or a database
                      based on it, it must continue to be licensed under the
                      Open Database License.
                    </p>
                  </div>
                </Stack>

                <Stack>
                  <Stack space="xs">
                    <h2 id="showcase" class="delta">
                      Showcase
                    </h2>
                    <p>
                      See how researchers, journalists, NGOs, and public
                      institutions use data from HowTheyVote.eu. Are you using
                      it as well? We’d love to hear from you!
                    </p>
                  </Stack>
                  <Showcase />
                </Stack>
              </Stack>
            </Wrapper>
          </div>
        </Stack>
      </BaseLayout>
    </App>
  );
};
