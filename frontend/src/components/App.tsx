import { ComponentChildren } from "preact";

import "../css/base.css";
import "../css/fonts.css";
import "../css/typography.css";
import "../css/utils.css";
import "../css/variables.css";

import { assetUrl } from "../lib/caching";

type AppProps = {
  children: ComponentChildren;
  title: string | Array<string | undefined | null>;
  head?: ComponentChildren;
  defaultCss?: boolean;
  defaultJs?: boolean;
};

export default function App({
  children,
  title,
  head,
  defaultCss = true,
  defaultJs = true,
}: AppProps) {
  const metaTitle = Array.isArray(title) ? title : [title];
  metaTitle.push("HowTheyVote.eu");

  return (
    <html lang="en">
      <head>
        <title>{metaTitle.filter(Boolean).join(" · ")}</title>

        {defaultCss && (
          <link rel="stylesheet" href={assetUrl("/dist/server.entry.css")} />
        )}

        <meta charSet="utf-8" />
        <meta
          name="viewport"
          content="width=device-width, initial-scale=1, viewport-fit=cover"
        />

        <link rel="icon" type="image/png" href="/static/favicon-32px.png" />
        <link rel="apple-touch-icon" href="/static/touch-icon-180px.png" />
        <link rel="manifest" href="/static/manifest.json" />
        <meta name="apple-mobile-web-app-title" content="HowTheyVote" />
        <meta name="apple-mobile-web-app-capable" content="yes" />
        <meta
          name="apple-mobile-web-app-status-bar-style"
          content="black-translucent"
        />
        <meta name="theme-color" content="var(--blue-darkest)" />

        {head}
      </head>
      <body>
        {children}
        {defaultJs && <script src={assetUrl("/dist/client.entry.js")} />}
      </body>
    </html>
  );
}
