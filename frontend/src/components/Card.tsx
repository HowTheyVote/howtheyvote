import type { ComponentChildren } from "preact";

import { bem } from "../lib/bem";

import "./Card.css";

type CardProps = {
  title: ComponentChildren;
  link: string;
  meta?: ComponentChildren;
  thumb?: ComponentChildren;
  action?: ComponentChildren;
  clickable?: boolean;
  className?: ComponentChildren;
};

export default function Card({
  title,
  link,
  meta,
  thumb,
  action,
  clickable = true,
  className,
}: CardProps) {
  return (
    <article class={`${bem("card", { clickable })} ${className || ""}`}>
      <div class="card__text">
        <h2 class="card__title">
          <a href={link}>{title}</a>
        </h2>
        {meta && <div class="card__meta">{meta}</div>}
      </div>
      {thumb && <div class="card__thumb">{thumb}</div>}
      {action && <div class="card__action">{action}</div>}
    </article>
  );
}
