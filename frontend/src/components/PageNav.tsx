import type { ComponentChildren, FunctionComponent } from "preact";
import Wrapper from "./Wrapper";

import "./PageNav.css";
import { useId } from "preact/hooks";

type PageNavProps = {
  children?: ComponentChildren;
};

const PageNav: FunctionComponent<PageNavProps> = ({ children }) => {
  const labelId = useId();

  return (
    <nav class="page-nav" aria-labelledby={labelId}>
      <div class="page-nav__scroll">
        <Wrapper className="page-nav__wrapper">
          <span id={labelId} class="page-nav__label">
            On this page:
          </span>
          <ul class="page-nav__items">{children}</ul>
        </Wrapper>
      </div>
    </nav>
  );
};

export default PageNav;
