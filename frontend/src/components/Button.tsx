import type { ComponentChildren, FunctionComponent, JSX } from "preact";
import { bem } from "../lib/bem";
import "./Button.css";

type ButtonProps = Omit<JSX.ButtonHTMLAttributes, "size"> & {
  size?: "lg" | "sm";
  style?: "fill" | "block" | "ghost";
  className?: string;
  children: ComponentChildren;
};

const Button: FunctionComponent<ButtonProps> = ({
  size,
  className,
  children,
  style,
  type = "button",
  ...rest
}: ButtonProps) => {
  return (
    <button
      type={type}
      className={`${bem("button", [size, style])} ${className || ""}`}
      {...rest}
    >
      {children}
    </button>
  );
};

export default Button;
