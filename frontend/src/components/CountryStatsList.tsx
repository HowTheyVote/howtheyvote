import type { Country, VotePositionCounts } from "../api";
import CountryFlag from "./CountryFlag";
import List from "./List";
import ListItem from "./ListItem";
import VoteResultChart from "./VoteResultChart";

type CountryStatsListProps = {
  countries: Array<{ country: Country; stats: VotePositionCounts }>;
};

type ItemProps = {
  country: Country;
  stats: VotePositionCounts;
};

function Item({ country, stats }: ItemProps) {
  const voted = stats.FOR + stats.AGAINST + stats.ABSTENTION;
  const total = voted + stats.DID_NOT_VOTE;
  const subtitle = (
    <span aria-hidden="true">
      {voted} of {total} MEPs voted.
    </span>
  );

  return (
    <ListItem
      title={
        <>
          {country.label}{" "}
          <span aria-hidden="true">
            <CountryFlag code={country.code} />
          </span>
        </>
      }
      subtitle={subtitle}
      chart={<VoteResultChart stats={stats} style="slim" />}
    />
  );
}

export default function CountryStatsList({ countries }: CountryStatsListProps) {
  return (
    <List truncate>
      {countries.map(({ country, stats }) => (
        <Item key={country.code} country={country} stats={stats} />
      ))}
    </List>
  );
}
