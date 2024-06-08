import { Source } from "../api";
import { formatDateTime } from "../lib/dates";
import List from "./List";
import ListItem from "./ListItem";

type SourcesProps = {
  sources: Array<Source>;
};

export default function Sources({ sources }: SourcesProps) {
  return (
    <List space="xxs">
      {sources.map((source) => (
        <SourceItem source={source} />
      ))}
    </List>
  );
}

function SourceItem({ source }: { source: Source }) {
  return (
    <ListItem
      key={source.url}
      link={source.url}
      title={source.name}
      subtitle={`accessed on ${formatDateTime(new Date(source.accessed_at))}`}
    />
  );
}
