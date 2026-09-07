import type { Group, VotePositionCounts } from "../api";
import Avatar from "./Avatar";
import List from "./List";
import ListItem from "./ListItem";
import VoteResultChart from "./VoteResultChart";

type GroupStatsListProps = {
  groups: Array<{ group: Group; stats: VotePositionCounts }>;
};

type ItemProps = {
  group: Group;
  stats: VotePositionCounts;
};

function Item({ group, stats }: ItemProps) {
  const avatarUrl = `/static/groups/${group.code.toLowerCase()}.svg`;
  const voted = stats.FOR + stats.AGAINST + stats.ABSTENTION;
  const total = voted + stats.DID_NOT_VOTE;
  const subtitle = (
    <span aria-hidden="true">
      {voted} of {total} MEPs voted.
    </span>
  );

  return (
    <ListItem
      title={`${group.label}`}
      subtitle={subtitle}
      avatar={<Avatar url={avatarUrl} style="square" />}
      chart={<VoteResultChart stats={stats} style="slim" includeNoShows={true} />}
    />
  );
}

export default function GroupStatsList({ groups }: GroupStatsListProps) {
  return (
    <List>
      {groups.map(({ group, stats }) => (
        <Item key={group.code} group={group} stats={stats} />
      ))}
    </List>
  );
}
