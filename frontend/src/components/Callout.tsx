import type { ComponentChildren } from "preact";
import Wrapper from "./Wrapper";

import "./Callout.css";

type CalloutProps = {
  children?: ComponentChildren;
};

export default function Callout({ children }: CalloutProps) {
  return (
    <div class="callout px">
      <Wrapper>{children}</Wrapper>
    </div>
  );
}
