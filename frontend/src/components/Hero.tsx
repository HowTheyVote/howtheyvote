import type { ComponentChildren } from "preact";
import "./Hero.css";
import Wrapper from "./Wrapper";

type HeroProps = {
  title: string;
  text?: string;
  action?: ComponentChildren;
};

export default function Hero({ title, text, action }: HeroProps) {
  return (
    <div class="hero">
      <div class="px">
        <Wrapper>
          <div class="hero__text">
            <h1 class="alpha hero__title">{title}</h1>
            {text && <p>{text}</p>}
          </div>
        </Wrapper>
      </div>
      {action && (
        <div class="hero__action px">
          <Wrapper>{action}</Wrapper>
        </div>
      )}
    </div>
  );
}
