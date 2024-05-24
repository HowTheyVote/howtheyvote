import { ComponentChildren, toChildArray } from "preact";
import { useState } from "preact/hooks";
import { bem } from "../lib/bem";
import Button from "./Button";
import "./List.css";

type ListProps = {
  truncate?: boolean;
  children: ComponentChildren;
  space?: "xxs";
};

export default function List({ truncate, children, space }: ListProps) {
  const [expanded, setExpanded] = useState(false);

  const listItems =
    truncate && !expanded ? toChildArray(children).slice(0, 10) : children;

  return (
    <div className={bem("list", [truncate && !expanded && "truncated", space])}>
      <ul>{listItems}</ul>
      {truncate && (
        <Button
          size="lg"
          className="list__toggle"
          onClick={() => setExpanded(!expanded)}
        >
          {expanded ? "Show less" : "Show all"}
        </Button>
      )}
    </div>
  );
}
