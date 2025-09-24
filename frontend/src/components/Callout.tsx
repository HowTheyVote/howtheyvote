import type { ComponentChildren } from "preact";

import "./Callout.css";

type CalloutProps = {
  title: string;
  children?: ComponentChildren;
  className?: string;
};

export default function Disclosure({
  title,
  children,
  className,
}: CalloutProps) {
  return (
    <div className={`callout ${className || ""}`}>
      <p>{title}</p>
      {children}
    </div>
  );
}
