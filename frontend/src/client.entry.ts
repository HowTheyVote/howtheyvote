import Banner from "./components/Banner";
import CountryStatsList from "./components/CountryStatsList";
import Eyes from "./components/Eyes";
import GroupStatsList from "./components/GroupStatsList";
import MemberVotesList from "./components/MemberVotesList";
import SearchActions from "./components/SearchActions";
import ShareButton from "./components/ShareButton";
import VoteTabs from "./components/VoteTabs";
import { hydrateIslands } from "./lib/islands";

hydrateIslands([
  MemberVotesList,
  GroupStatsList,
  CountryStatsList,
  VoteTabs,
  Eyes,
  ShareButton,
  Banner,
  SearchActions,
]);
