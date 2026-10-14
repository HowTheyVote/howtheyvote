import type { ComponentChildren } from "preact";

import { bem } from "../lib/bem";

import "./Card.css";

type CardProps = {
  title: ComponentChildren;
  link: string;
  subtitle?: ComponentChildren;
  meta?: ComponentChildren;
  description?: ComponentChildren;
  thumb?: ComponentChildren;
  action?: ComponentChildren;
  clickable?: boolean;
  external?: boolean;
  className?: ComponentChildren;
};

export default function Card({
  title,
  subtitle,
  link,
  meta,
  description,
  thumb,
  action,
  clickable = true,
  external = false,
  className,
}: CardProps) {
  return (
    <article class={`${bem("card", { clickable })} ${className || ""}`}>
      <div class="card__text">
        <h2 class="card__title">
          <a
            href={link}
            target={external ? "_blank" : undefined}
            rel={external ? "noreferrer noopener" : undefined}
          >
            {title}
          </a>
        </h2>
        {subtitle && <div class="card__subtitle">{subtitle}</div>}
        {meta && <div class="card__meta">{meta}</div>}
        {description && <p class="card__description">{description}</p>}
      </div>
      {thumb && <div class="card__thumb">{thumb}</div>}
      {action && <div class="card__action">{action}</div>}
    </article>
  );
}
