import type { ComponentChildren } from "preact";
import { bem } from "../lib/bem";
import "./Footer.css";

type FooterProps = {
  style?: "dark";
  copyright?: ComponentChildren;
};

export default function Footer({ style, copyright }: FooterProps) {
  return (
    <footer className={bem("footer", style)}>
      <ul>
        <li>
          <a
            href="https://github.com/HowTheyVote/howtheyvote"
            target="_blank"
            rel="noopener noreferrer"
          >
            GitHub
          </a>
        </li>
        <li>
          <a
            href="https://eupolicy.social/@HowTheyVoteEU"
            target="_blank"
            rel="noopener noreferrer me"
          >
            Mastodon
          </a>
        </li>
        <li>
          <a href="/about#license">License</a>
        </li>
        <li>
          <a href="/imprint">Imprint & Privacy</a>
        </li>
      </ul>

      {copyright && <div class="footer__copyright">{copyright}</div>}
    </footer>
  );
}
