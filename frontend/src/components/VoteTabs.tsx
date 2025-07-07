import type { VoteStatsByCountry, VoteStatsByGroup } from "../api";
import {
  deserializeMemberVotes,
  type SerializedMemberVotes,
} from "../lib/serialization";
import CountryStatsList from "./CountryStatsList";
import GroupStatsList from "./GroupStatsList";
import MemberVotesList from "./MemberVotesList";
import Tabs from "./Tabs";

type VoteTabsProps = {
  memberVotes: SerializedMemberVotes;
  groupStats: Array<VoteStatsByGroup>;
  countryStats: Array<VoteStatsByCountry>;
};

export default function VoteTabs({
  memberVotes,
  countryStats,
  groupStats,
}: VoteTabsProps) {
  return (
    <Tabs>
      <Tabs.Panel id="tab-members" label="MEPs">
        <MemberVotesList
          memberVotes={deserializeMemberVotes(memberVotes)}
          countries={countryStats.map(({ country }) => country)}
          groups={groupStats.map(({ group }) => group)}
        />
      </Tabs.Panel>
      <Tabs.Panel id="tab-groups" label="Political Groups">
        <GroupStatsList groups={groupStats} />
      </Tabs.Panel>
      <Tabs.Panel id="tab-countries" label="Countries">
        <CountryStatsList countries={countryStats} />
      </Tabs.Panel>
    </Tabs>
  );
}
