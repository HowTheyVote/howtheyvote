import App from "../components/App";
import * as config from "../config";

declare global {
  namespace preact.createElement.JSX {
    interface IntrinsicElements {
      // biome-ignore lint/suspicious/noExplicitAny: There are no types available for this web component
      "elements-api": any;
    }
  }
}

export function DevelopersPage() {
  return (
    <App
      title={"Developers"}
      defaultCss={false}
      defaultJs={false}
      head={
        <>
          <script src="/static/spotlight/8.1.0/web-components.min.js" />
          <link
            rel="stylesheet"
            href="/static/spotlight/8.1.0/styles.min.css"
          />
        </>
      }
    >
      <elements-api
        basePath="/developers"
        apiDescriptionUrl={config.BACKEND_PUBLIC_URL}
        router="history"
        layout="sidebar"
        style="display: block; min-height: 100vh;"
      />
    </App>
  );
}
