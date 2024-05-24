import { useState } from "preact/hooks";
import { Country, Group, Member, MemberVote } from "../api";
import { normalize } from "../lib/normalization";
import Avatar from "./Avatar";
import Button from "./Button";
import CountriesFilterSelect from "./CountriesFilterSelect";
import EmptyState from "./EmptyState";
import GroupsFilterSelect from "./GroupsFilterSelect";
import Input from "./Input";
import List from "./List";
import ListItem from "./ListItem";
import PositionFilterSelect from "./PositionFilterSelect";
import Thumb from "./Thumb";

import "./MemberVotesList.css";

type MemberVotesListProps = {
  memberVotes: Array<MemberVote>;
  groups: Array<Group>;
  countries: Array<Country>;
};

type ItemProps = {
  member: Member;
  position: MemberVote["position"];
};

function Item({ member, position }: ItemProps) {
  const subtitle = (
    <>
      <abbr title={member.group?.label}>{member.group?.short_label}</abbr>
      {" · "}
      {member.country.label}
    </>
  );

  return (
    <ListItem
      key={member.id}
      title={`${member.first_name} ${member.last_name}`}
      subtitle={subtitle}
      avatar={member.thumb_url && <Avatar url={member.thumb_url} />}
      thumb={<Thumb position={position} style="circle" />}
    />
  );
}

export default function MemberVotesList({
  memberVotes,
  groups,
  countries,
}: MemberVotesListProps) {
  const [query, setQuery] = useState("");
  const [selectedGroup, setGroup] = useState("");
  const [selectedCountry, setCountry] = useState("");
  const [selectedPosition, setPosition] = useState("");

  const resetFilters = () => {
    setQuery("");
    setGroup("");
    setCountry("");
    setPosition("");
  };

  const filteredMemberVotes = filterMemberVotes(memberVotes, {
    query,
    selectedGroup,
    selectedCountry,
    selectedPosition,
  });

  return (
    <div class="member-votes-list">
      <div class="member-votes-list__action-bar">
        <label class="member-votes-list__search">
          <span class="visually-hidden">Filter by name</span>
          <Input
            type="search"
            placeholder="Filter by name"
            value={query}
            autoComplete="off"
            onInput={(event) => setQuery(event.currentTarget.value)}
          />
        </label>

        <label>
          <span class="visually-hidden">Filter by political group</span>
          <GroupsFilterSelect
            groups={groups}
            value={selectedGroup}
            onChange={(event) => setGroup(event.currentTarget.value)}
          />
        </label>

        <label>
          <span class="visually-hidden">Filter by country</span>
          <CountriesFilterSelect
            countries={countries}
            value={selectedCountry}
            onChange={(event) => setCountry(event.currentTarget.value)}
          />
        </label>

        <label>
          <span class="visually-hidden">Filter by vote position</span>
          <PositionFilterSelect
            value={selectedPosition}
            onChange={(event) => setPosition(event.currentTarget.value)}
          />
        </label>
      </div>

      {filteredMemberVotes.length > 0 ? (
        <List truncate={filteredMemberVotes.length > 10}>
          {filteredMemberVotes.map(({ member, position }) => (
            <Item key={member.id} member={member} position={position} />
          ))}
        </List>
      ) : (
        <EmptyState
          action={<Button onClick={() => resetFilters()}>Reset filters</Button>}
        >
          None of the MEPs match your filter criteria.
        </EmptyState>
      )}
    </div>
  );
}

type FilterConfig = {
  query: string;
  selectedGroup: string;
  selectedCountry: string;
  selectedPosition: string;
};

function filterMemberVotes(
  memberVotes: Array<MemberVote>,
  { query, selectedGroup, selectedCountry, selectedPosition }: FilterConfig,
) {
  return memberVotes.filter(({ member, position }) => {
    const fullName = `${member.first_name} ${member.last_name}`;

    if (!normalize(fullName).includes(normalize(query))) {
      return false;
    }

    if (selectedGroup && member.group?.code !== selectedGroup) {
      return false;
    }

    if (selectedCountry && member.country.code !== selectedCountry) {
      return false;
    }

    if (selectedPosition && position !== selectedPosition) {
      return false;
    }

    return true;
  });
}
