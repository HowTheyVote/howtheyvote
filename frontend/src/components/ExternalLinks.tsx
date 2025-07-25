import type { Link } from "../api";
import List from "./List";
import ListItem from "./ListItem";

type ExternalLinksProps = {
  links: Array<Link>;
};

export default function ExternalLinks({ links }: ExternalLinksProps) {
  return (
    <List>
      {links.map((link) => (
        <ListItem
          key={link.url}
          link={link.url}
          title={link.title}
          subtitle={link.description}
        />
      ))}
    </List>
  );
}
