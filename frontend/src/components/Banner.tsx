import type { ComponentChildren } from "preact";
import Wrapper from "./Wrapper";

import "./Banner.css";

type BannerProps = {
  children?: ComponentChildren;
};

export default function Banner({ children }: BannerProps) {
  return (
    <div class="banner px">
      <Wrapper>{children}</Wrapper>
    </div>
  );
}
