import type { JSX } from "preact";
import type { MemberVote, Vote } from "../api";
import { bem } from "../lib/bem";
import Icon from "./Icon";

import "./Thumb.css";

type ThumbProps = JSX.HTMLAttributes<HTMLDivElement> & {
  style?: "circle";
} & (
    | {
        position: MemberVote["position"];
        result?: never;
      }
    | {
        result: NonNullable<Vote["result"]>;
        position?: never;
      }
  );

export default function Thumb({
  position,
  result,
  style,
  className,
}: ThumbProps) {
  const modifier = (position || result).toLowerCase().replaceAll("_", "-");
  const label = (position || result).toLowerCase().replaceAll("_", " ");

  return (
    <span
      className={`${bem("thumb", [modifier, style])} ${className || ""}`}
      title={label}
    >
      {position !== "DID_NOT_VOTE" && (
        <Icon name="thumb" className="thumb__icon" />
      )}
      <span class="visually-hidden">{label}</span>
    </span>
  );
}
