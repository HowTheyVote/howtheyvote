import { ComponentChildren } from "preact";
import { bem } from "../lib/bem";
import "./Stack.css";

type StackProps = {
  children?: ComponentChildren;
  space?: "xl" | "lg" | "xs" | "sm" | "xs" | "xxs";
};

export default function Stack({ space, children }: StackProps) {
  return <div className={bem("stack", space)}>{children}</div>;
}
