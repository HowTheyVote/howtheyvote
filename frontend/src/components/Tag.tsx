import type { ComponentProps, JSX } from "preact";
import Icon from "./Icon";

import "./Tag.css";

type TagProps<T extends keyof JSX.IntrinsicElements> = {
  as: T;
  deleteLink?: string;
  deleteLabel?: string;
} & ComponentProps<T>;

function Tag<T extends keyof JSX.IntrinsicElements>({
  as: Component = "span",
  children,
  deleteLink,
  deleteLabel,
  ...rest
}: TagProps<T>) {
  return (
    <Component class="tag" {...rest}>
      <span class="tag__label">{children}</span>
      {deleteLink && (
        <a href={deleteLink} class="tag__delete">
          <span class="visually-hidden">{deleteLabel || "Delete"}</span>
          <Icon className="search-filter-pill__icon" name="close" />
        </a>
      )}
    </Component>
  );
}

export default Tag;
