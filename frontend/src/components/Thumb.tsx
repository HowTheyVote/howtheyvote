import type { JSX } from "preact";
import type { MemberVote } from "../api";
import { bem } from "../lib/bem";

import "./Thumb.css";

type ThumbProps = JSX.HTMLAttributes<HTMLDivElement> & {
  position: MemberVote["position"];
  style?: "circle";
};

export default function Thumb({ position, style, className }: ThumbProps) {
  const modifier = position.toLowerCase().replaceAll("_", "-");
  const label = position.toLowerCase().replaceAll("_", " ");

  return (
    <span
      className={`${bem("thumb", [modifier, style])} ${className || ""}`}
      title={label}
    >
      {position !== "DID_NOT_VOTE" && (
        <svg aria-hidden="true">
          <use href="/static/icons.svg#thumb" />
        </svg>
      )}
    </span>
  );
}
