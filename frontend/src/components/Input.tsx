import type { JSX } from "preact";
import { bem } from "../lib/bem";

import "./Input.css";

type InputProps = Omit<JSX.InputHTMLAttributes, "size"> & {
  size?: "lg";
  className?: string;
};

export default function Input({
  type = "text",
  size,
  className,
  ...rest
}: InputProps) {
  return (
    <input
      type={type}
      className={`${bem("input", size)} ${className || ""}`}
      {...rest}
    />
  );
}
