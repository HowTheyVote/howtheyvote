import type { ComponentChildren } from "preact";
import { useId } from "preact/hooks";

import { bem } from "../lib/bem";

import "./Card.css";

type CardProps = {
  title: ComponentChildren;
  link: string;
  subtitle?: ComponentChildren;
  meta?: ComponentChildren;
  thumb?: ComponentChildren;
  action?: ComponentChildren;
  clickable?: boolean;
  className?: ComponentChildren;
};

export default function Card({
  title,
  link,
  subtitle,
  meta,
  thumb,
  action,
  clickable = true,
  className,
}: CardProps) {
  const subtitleId = useId();

  return (
    <article class={`${bem("card", { clickable })} ${className || ""}`}>
      <div class="card__text">
        <h2 class="card__title">
          <a href={link} aria-describedby={subtitle ? subtitleId : undefined}>
            {title}
          </a>
        </h2>
        {subtitle && (
          <p id={subtitleId} class="card__subtitle">
            {subtitle}
          </p>
        )}
        {meta && <div class="card__meta">{meta}</div>}
      </div>
      {thumb && <div class="card__thumb">{thumb}</div>}
      {action && <div class="card__action">{action}</div>}
    </article>
  );
}
