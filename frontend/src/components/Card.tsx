import type { ComponentChildren } from "preact";

import "./Card.css";

type CardProps = {
  title: ComponentChildren;
  link: string;
  meta?: ComponentChildren;
  thumb?: ComponentChildren;
};

export default function Card({ title, link, meta, thumb }: CardProps) {
  return (
    <article class="card">
      <div class="card__text">
        <h2 class="card__title">
          <a href={link}>{title}</a>
        </h2>
        {meta && <div class="card__meta">{meta}</div>}
      </div>
      {thumb && <div class="card__thumb">{thumb}</div>}
    </article>
  );
}
