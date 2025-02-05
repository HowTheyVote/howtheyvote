import Banner from "./components/Banner";
import CountryStatsList from "./components/CountryStatsList";
import Eyes from "./components/Eyes";
import GroupStatsList from "./components/GroupStatsList";
import MemberVotesList from "./components/MemberVotesList";
import ShareButton from "./components/ShareButton";
import SortSelect from "./components/SortSelect";
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
  SortSelect,
]);
