import type { ComponentChildren } from "preact";
import { bem } from "../lib/bem";

import "./Tag.css";

type TagProps = {
  style?: "featured";
  children: ComponentChildren;
};

function Tag({ style, children }: TagProps) {
  return <span className={bem("tag", style)}>{children}</span>;
}

export default Tag;
