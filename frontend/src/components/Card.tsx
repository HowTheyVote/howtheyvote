import type { ComponentChildren } from "preact";
import { useId } from "preact/hooks";

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
  headingLevel?: "h2" | "h3" | "h4";
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
  headingLevel = "h2",
  clickable = true,
  external = false,
  className,
}: CardProps) {
  const Heading = headingLevel;
  const subtitleId = useId();

  return (
    <article class={`${bem("card", { clickable })} ${className || ""}`}>
      <div class="card__text">
        <Heading class="card__title">
          <a
            href={link}
            target={external ? "_blank" : undefined}
            rel={external ? "noreferrer noopener" : undefined}
            aria-describedby={subtitle ? subtitleId : undefined}
          >
            {title}
          </a>
        </Heading>
        {subtitle && (
          <div id={subtitleId} class="card__subtitle">
            {subtitle}
          </div>
        )}
        {meta && <div class="card__meta">{meta}</div>}
        {description && <p class="card__description">{description}</p>}
      </div>
      {thumb && <div class="card__thumb">{thumb}</div>}
      {action && <div class="card__action">{action}</div>}
    </article>
  );
}
