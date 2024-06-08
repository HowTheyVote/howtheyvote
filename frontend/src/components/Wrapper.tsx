import { ComponentChildren } from "preact";

import "./Wrapper.css";

type WrapperProps = {
  children: ComponentChildren;
  className?: string;
};

export default function Wrapper({ children, className }: WrapperProps) {
  return <div className={`wrapper ${className || ""}`}>{children}</div>;
}
