import App from "../components/App";
import BaseLayout from "../components/BaseLayout";
import Hero from "../components/Hero";
import Stack from "../components/Stack";
import Wrapper from "../components/Wrapper";
import { Page } from "../lib/server";

export const ImprintPage: Page = () => {
  return (
    <App title={"Imprint & Privacy"}>
      <BaseLayout>
        <Stack space="lg">
          <Hero title="Imprint & Privacy" />
          <div class="px">
            <Wrapper>
              <div class="prose">
                <h2 class="beta">Imprint</h2>

                <p>This website is operated by:</p>

                <p>
                  HowTheyVote.eu
                  <br />
                  Till Prochaska, Linus Hagemann
                  <br />
                  c/o Cultivation Space, Aufgang 4<br />
                  Gottschedstraße 4<br />
                  13357 Berlin
                </p>

                <p>
                  You can contact us by sending an email to mail [at]
                  howtheyvote.eu.
                </p>

                <h2 class="beta">Privacy notice</h2>

                <p>
                  We limit the amount of personal data that we process as much
                  as possible. We process personal information only with your
                  consent or when it’s necessary to provide this service.
                </p>

                <h3 class="gamma">Access data</h3>

                <p>
                  When you request a page from HowTheyVote.eu, your device
                  automatically transfers certain information to our server:
                </p>

                <ul>
                  <li>Operating system</li>
                  <li>Browser type</li>
                  <li>Your IP address</li>
                  <li>Your language preferences</li>
                  <li>URL from which you’ve accessed HowTheyVote.eu</li>
                </ul>

                <p>
                  This information is strictly necessary in order to provide you
                  access to HowTheyVote.eu. We do not keep access logfiles or
                  store this information in any other way after processing your
                  request.
                </p>

                <p>
                  The legal basis for processing the personal information is
                  Article 6(1)(f) GDPR.
                </p>

                <h3 class="gamma">Data error report form</h3>

                <p>
                  We provide a form that you can use to contact us if you have
                  found an error in our data. You can submit this form without
                  providing personal information such as your name or email
                  address.
                </p>

                <p>
                  We use a subprocessor, Tally, August van Lokerenstraat 71,
                  9050 Gent, Belgium, to provide the form and collect form
                  submissions. When you access or submit the form the
                  subprocessor processes personal information. You can learn
                  more about how Tally processes personal data in{" "}
                  <a href="https://tally.so/help/privacy-policy">
                    Tally’s privacy policy
                  </a>
                  .
                </p>

                <h3 class="gamma">Members of the European Parliament</h3>

                <p>
                  We collect and store the following personal information about
                  Members of the European Parliament (MEPs) in order to provide
                  access to and archive information about legislative and
                  non-legislative procedures. We only collect and store
                  information made publicly available by institutions of the
                  European Union.
                </p>

                <ul>
                  <li>Name</li>
                  <li>Nationality</li>
                  <li>Date of birth</li>
                  <li>Duration of membership</li>
                  <li>Political group memberships</li>
                  <li>Email address</li>
                  <li>Facebook profile</li>
                  <li>Twitter profile</li>
                </ul>

                <p>
                  The legal basis for processing the personal information is
                  Article 6(1)(e) GDPR.
                </p>

                <h3 class="gamma">Name and address of the controller</h3>

                <p>
                  HowTheyVote.eu
                  <br />
                  Till Prochaska, Linus Hagemann
                  <br />
                  c/o Cultivation Space, Aufgang 4<br />
                  Gottschedstraße 4<br />
                  13357 Berlin
                </p>

                <p>
                  You can contact us by sending an email to mail [at]
                  howtheyvote.eu.
                </p>

                <h3 class="gamma">Your rights</h3>

                <ul>
                  <li>
                    You are entitled to receive information about the personal
                    data stored about you and have the right to correction,
                    blocking, and erasure of your personal information.
                  </li>
                  <li>
                    If we process your personal information with your consent
                    you also have the right to withdraw consent at any time.
                  </li>
                  <li>
                    In addition, you also have the right to lodge a complaint
                    with a supervisory authority.
                  </li>
                </ul>

                <h3 class="gamma">Updates</h3>

                <p>
                  We reserve the right to change this privacy notice at any time
                  in compliance with legal requirements.
                </p>
              </div>
            </Wrapper>
          </div>
        </Stack>
      </BaseLayout>
    </App>
  );
};
