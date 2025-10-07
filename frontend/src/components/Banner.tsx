import { useState } from "preact/hooks";
import Icon from "./Icon";
import Wrapper from "./Wrapper";

import "./Banner.css";

const STORAGE_KEY = "survey-banner-dismissed";

export default function Banner() {
  const [isDismissed, setIsDismissed] = useState<boolean>(
    typeof window === "undefined"
      ? true // Don't render on the server
      : window.localStorage.getItem(STORAGE_KEY) === "true",
  );

  const onClose = () => {
    setIsDismissed(true);
    window.localStorage.setItem(STORAGE_KEY, "true");
  };

  if (isDismissed) {
    return null;
  }

  return (
    <div className="Banner">
      <Wrapper className="Banner__wrapper">
        Answer <strong>3 quick questions</strong> to help us improve
        HowTheyVote.eu.{" "}
        <a
          href="https://tally.so/r/w740y2"
          target="_blank"
          rel="noopener noreferrer"
        >
          Fill out survey
        </a>
        <button type="button" className="Banner__close" onClick={onClose}>
          <span class="visually-hidden">Close</span>
          <Icon name="close" className="Banner__icon" />
        </button>
      </Wrapper>
    </div>
  );
}
