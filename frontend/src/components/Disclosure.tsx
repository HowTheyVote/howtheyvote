import type { ComponentChildren } from "preact";
import Icon from "./Icon";

import "./Disclosure.css";

type DisclosureProps = {
  title: ComponentChildren;
  children?: ComponentChildren;
};

export default function Disclosure({ title, children }: DisclosureProps) {
  return (
    <details class="disclosure">
      <summary>
        <span>{title}</span>
        <Icon name="chevron-down" className="disclosure__icon" />
      </summary>
      <div class="disclosure__content">{children}</div>
    </details>
  );
}
