import type { ComponentChildren } from "preact";
import Icon from "./Icon";

import "./Tag.css";

type TagProps = {
  children: ComponentChildren;
  deleteLink?: string;
  deleteLabel?: string;
};

function Tag({ children, deleteLink, deleteLabel }: TagProps) {
  return (
    <span class="tag">
      <span class="tag__label">{children}</span>
      {deleteLink && (
        <a href={deleteLink} class="tag__delete">
          <span class="visually-hidden">{deleteLabel || "Delete"}</span>
          <Icon className="search-filter-pill__icon" name="close" />
        </a>
      )}
    </span>
  );
}

export default Tag;
