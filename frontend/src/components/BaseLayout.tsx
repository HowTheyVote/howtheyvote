import type { ComponentChildren } from "preact";
import { bem } from "../lib/bem";
import { Island } from "../lib/islands";
import Banner from "./Banner";
import Footer from "./Footer";
import Header from "./Header";
import Wrapper from "./Wrapper";

import "./BaseLayout.css";

type BaseLayoutProps = {
  children: ComponentChildren;
  header?: ComponentChildren;
  footer?: ComponentChildren;
  style?: "dark";
};

export default function BaseLayout({
  children,
  header,
  footer,
  style,
}: BaseLayoutProps) {
  header = header || <Header />;
  footer = footer || <Footer />;

  return (
    <div className={bem("base-layout", style)}>
      <Island>
        <Banner />
      </Island>
      {header}
      <main className="base-layout__main">{children}</main>
      <Wrapper className="base-layout__footer">{footer}</Wrapper>
    </div>
  );
}
