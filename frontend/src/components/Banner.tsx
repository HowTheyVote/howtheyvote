import { useState } from "preact/hooks";
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
          <svg
            xmlns="http://www.w3.org/2000/svg"
            xmlnsXlink="http://www.w3.org/1999/xlink"
            viewBox="0 0 16 16"
            aria-hidden="true"
          >
            <path d="M14.7,1.3c-0.4-0.4-1-0.4-1.4,0L8,6.6L2.7,1.3c-0.4-0.4-1-0.4-1.4,0s-0.4,1,0,1.4L6.6,8l-5.3,5.3c-0.4,0.4-0.4,1,0,1.4C1.5,14.9,1.7,15,2,15s0.5-0.1,0.7-0.3L8,9.4l5.3,5.3c0.2,0.2,0.5,0.3,0.7,0.3s0.5-0.1,0.7-0.3c0.4-0.4,0.4-1,0-1.4L9.4,8l5.3-5.3C15.1,2.3,15.1,1.7,14.7,1.3z" />
          </svg>
        </button>
      </Wrapper>
    </div>
  );
}
