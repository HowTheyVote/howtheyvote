import { FunctionComponent, VNode } from "preact";
import App from "../components/App";
import Eyes from "../components/Eyes";
import { HTTPException } from "../lib/http";
import { Island } from "../lib/islands";

import "./ErrorPage.css";

type ErrorPageMessages = Record<
  number,
  {
    title: string;
    message: string | VNode;
  }
>;

const CONTENT: ErrorPageMessages = {
  404: {
    title: "We can’t find this page",
    message: (
      <>
        Try <a href="/votes">searching</a> our database or
        <br />
        view <a href="/votes">recent votes</a> instead.
      </>
    ),
  },
  500: {
    title: "Internal Server Error",
    message:
      "Something went wrong. We’ve already been informed of the error and will fix it as soon as possible.",
  },
};

export const ErrorPage: FunctionComponent<{ error: Error }> = ({ error }) => {
  let content;

  if (error instanceof HTTPException) {
    content = CONTENT[error.code];
  }

  if (!content) {
    content = CONTENT[500];
  }

  return (
    <App title={"Error"}>
      <div class="error-page">
        <Island>
          <Eyes />
        </Island>
        <div class="error-page__wrapper">
          <h1 class="error-page__title alpha">{content.title}</h1>
          <p class="error-page__message">{content.message}</p>
        </div>
      </div>
    </App>
  );
};
