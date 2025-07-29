import type { ComponentChildren, FunctionComponent } from "preact";

type PageNavItemProps = {
  href: string;
  children?: ComponentChildren;
};

const PageNavItem: FunctionComponent<PageNavItemProps> = ({
  href,
  children,
}) => (
  <li>
    <a href={href}>{children}</a>
  </li>
);

export default PageNavItem;
