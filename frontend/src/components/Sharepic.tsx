import type { ComponentChildren } from "preact";

import "./Sharepic.css";

type SharepicProps = {
  children?: ComponentChildren;
};

function Sharepic({ children }: SharepicProps) {
  return <div class="sharepic">{children}</div>;
}

export default Sharepic;
