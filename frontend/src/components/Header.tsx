import { bem } from "../lib/bem";
import Wrapper from "./Wrapper";

import "./Header.css";

type HeaderProps = {
  style?: "dark";
};

export default function Header({ style }: HeaderProps) {
  return (
    <header className={bem("header", style)}>
      <Wrapper className="header__wrapper">
        <a className="header__logotype" href="/">
          HowTheyVote.eu
        </a>
        <nav className="header__nav">
          <ul>
            <li>
              <a href="/votes">All Votes</a>
            </li>
            <li>
              <a href="/about">About & FAQ</a>
            </li>
          </ul>
        </nav>
      </Wrapper>
    </header>
  );
}
