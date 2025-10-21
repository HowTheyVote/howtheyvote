import sirv from "sirv";
import { redirect } from "./lib/http";
import { App, isBot, logRequests, noMatchHandler, onError } from "./lib/server";
import { AboutPage, loader as aboutLoader } from "./pages/AboutPage";
import { DevelopersPage } from "./pages/DevelopersPage";
import { HomePage, loader as homeLoader } from "./pages/HomePage";
import { ImprintPage } from "./pages/ImprintPage";
import { SearchPage, loader as searchLoader } from "./pages/SearchPage";
import {
  ShowAmendmentVotesPage,
  loader as showAmendmentVotesLoader,
} from "./pages/ShowAmendmentVotesPage";
import { ShowVotePage, loader as showVoteLoader } from "./pages/ShowVotePage";
import {
  VoteSharepicPage,
  loader as voteSharepicLoader,
} from "./pages/VoteSharepicPage";

const app = new App({ onError, noMatchHandler });

const distMiddleware = sirv("dist");
const staticMiddleware = sirv("static");
app.use("dist/", distMiddleware);
app.use("static/", staticMiddleware);
app.use(isBot);
app.use(logRequests);

app.registerPage("/", HomePage, homeLoader);
app.registerPage("/votes", SearchPage, searchLoader);
app.registerPage("/votes/:id", ShowVotePage, showVoteLoader);
app.registerPage(
  "/votes/:id/amendments",
  ShowAmendmentVotesPage,
  showAmendmentVotesLoader,
);
app.registerPage("/votes/:id/sharepic", VoteSharepicPage, voteSharepicLoader);
app.registerPage(["/developers", "/developers/*"], DevelopersPage);
app.registerPage("/imprint", ImprintPage);
app.registerPage("/about", AboutPage, aboutLoader);

// Redirect vote shortlinks (e.g. howtheyvote.eu/162190)
const voteIdRegex = /^[0-9]{6}$/;
app.get("/:id", (request, _response, next) => {
  const voteId = request.params.id;

  if (!voteIdRegex.test(voteId)) {
    return next?.();
  }

  redirect(`/votes/${voteId}`);
});

app.listen(8000, () => {}, "::");
