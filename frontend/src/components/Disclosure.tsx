import type { ComponentChildren } from "preact";

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
        <svg
          aria-hidden="true"
          xmlns="http://www.w3.org/2000/svg"
          xmlnsXlink="http://www.w3.org/1999/xlink"
          viewBox="0 0 12 12"
          width="12"
          height="12"
        >
          <path d="M10.293,3.293,6,7.586,1.707,3.293A1,1,0,0,0,.293,4.707l5,5a1,1,0,0,0,1.414,0l5-5a1,1,0,1,0-1.414-1.414Z" />
        </svg>
      </summary>
      <div class="disclosure__content">{children}</div>
    </details>
  );
}
