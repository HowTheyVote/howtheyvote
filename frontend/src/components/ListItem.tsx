import type { ComponentChildren, FunctionComponent } from "preact";
import "./ListItem.css";

type ListItemProps = {
  title: ComponentChildren;
  link?: string;
  subtitle?: ComponentChildren;
  avatar?: ComponentChildren;
  thumb?: ComponentChildren;
  chart?: ComponentChildren;
};

const ListItem: FunctionComponent<ListItemProps> = ({
  title,
  link,
  subtitle,
  avatar,
  thumb,
  chart,
}) => {
  const isExternal = link?.startsWith("https://");

  return (
    <li className="list-item">
      {avatar && <div className="list-item__avatar">{avatar}</div>}
      <div className="list-item__text">
        {link ? (
          <a
            href={link}
            target={isExternal ? "_blank" : undefined}
            rel={isExternal ? "noopener noreferrer" : undefined}
          >
            <strong>{title}</strong>
          </a>
        ) : (
          <strong>{title}</strong>
        )}
        <div className="list-item__subtitle">{subtitle}</div>
        {chart && <div className="list-item__chart">{chart}</div>}
      </div>
      {thumb && <div className="list-item__thumb">{thumb}</div>}
    </li>
  );
};

export default ListItem;
