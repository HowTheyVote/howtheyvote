import sirv from "sirv";
import { redirect } from "./lib/http";
import { App, isBot, logRequests, noMatchHandler, onError } from "./lib/server";
import { AboutPage, loader as aboutLoader } from "./pages/AboutPage";
import {
  AmendmentVotesPage,
  loader as amendmentVotesLoader,
} from "./pages/AmendmentVotesPage";
import { DevelopersPage } from "./pages/DevelopersPage";
import { HomePage, loader as homeLoader } from "./pages/HomePage";
import { ImprintPage } from "./pages/ImprintPage";
import { MemberPage, loader as memberLoader } from "./pages/MemberPage";
import {
  MemberSharepicPage,
  loader as memberSharepicLoader,
} from "./pages/MemberSharepicPage";
import { SearchPage, loader as searchLoader } from "./pages/SearchPage";
import { VotePage, loader as voteLoader } from "./pages/VotePage";
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
app.registerPage("/votes/:id", VotePage, voteLoader);
app.registerPage(
  "/votes/:id/amendments",
  AmendmentVotesPage,
  amendmentVotesLoader,
);
app.registerPage("/votes/:id/sharepic", VoteSharepicPage, voteSharepicLoader);
app.registerPage("/members/:id", MemberPage, memberLoader);
app.registerPage(
  "/members/:id/sharepic",
  MemberSharepicPage,
  memberSharepicLoader,
);
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
