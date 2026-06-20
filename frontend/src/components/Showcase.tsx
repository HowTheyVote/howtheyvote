import showcase from "../data/showcase.json";

import "./Showcase.css";

function Showcase() {
  return (
    <div class="showcase">
      {showcase.map(({ url, title, author, description }) => (
        <article class="showcase__item">
          <header>
            <h3 class="gamma">
              <a href={url} rel="noopener noreferrer" target="_blank">
                {title}
              </a>
            </h3>
            <p class="showcase__meta">{author}</p>
          </header>
          <p>{description}</p>
        </article>
      ))}
    </div>
  );
}

export default Showcase;
