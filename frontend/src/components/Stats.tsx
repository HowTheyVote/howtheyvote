import type { ComponentChildren } from "preact";

import "./Stats.css";

type StatsProps = {
  children?: ComponentChildren;
};

export default function Stats({ children }: StatsProps) {
  return <div class="stats">{children}</div>;
}
