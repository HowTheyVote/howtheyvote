import type { JSX } from "preact";
import { bem } from "../lib/bem";

import "./Button.css";

type ButtonProps<T extends "button" | "a"> = JSX.IntrinsicElements[T] & {
  as?: "button" | "a";
  size?: "lg" | "sm";
  style?: "fill" | "block" | "ghost";
  className?: string;
};

export default function Button<T extends "button" | "a">({
  as = "button",
  size,
  style,
  className,
  type = "button",
  children,
  ...rest
}: ButtonProps<T>) {
  const Component = as;

  return (
    <Component
      type={as === "button" ? type : undefined}
      className={`${bem("button", [size, style])} ${className || ""}`}
      // biome-ignore lint/suspicious/noExplicitAny: There is no sensible way to avoid this cast
      {...(rest as any)}
    >
      {children}
    </Component>
  );
}
