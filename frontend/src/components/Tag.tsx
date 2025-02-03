import type { ComponentChildren } from "preact";

import "./Tag.css";

type TagProps = {
  children: ComponentChildren;
};

function Tag({ children }: TagProps) {
  return <span className="tag">{children}</span>;
}

export default Tag;
