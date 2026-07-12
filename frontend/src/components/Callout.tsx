import type { ComponentChildren } from "preact";

import "./Callout.css";

type CalloutProps = {
  children?: ComponentChildren;
};

export default function Callout({ children }: CalloutProps) {
  return <div class="callout">{children}</div>;
}
