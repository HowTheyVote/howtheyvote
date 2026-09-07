import "./DataProducts.css";

function DataProducts() {
  return (
    <div class="data-products">
      <article class="data-products__product">
        <h3 class="gamma">Dataset</h3>
        <p>
          Download a full copy of our data as a set of CSV files, updated on a
          weekly basis. Perfect for large-scale data analysis.
        </p>
        <p class="data-products__action">
          <a
            href="https://github.com/howtheyvote/data"
            rel="noopener noreferrer"
            target="_blank"
          >
            Download & Documentation
          </a>
        </p>
      </article>
      <article class="data-products__product">
        <h3 class="gamma">API</h3>
        <p>
          Get real-time access to the latest votes or search for votes by
          keyword.
        </p>
        <p class="data-products__action">
          <a href="/developers">Documentation</a>
        </p>
      </article>
      <article class="data-products__product">
        <h3 class="gamma">Download vote results</h3>
        <p>
          Download the results of a single vote in JSON or CSV formats, ready to
          be opened in Excel and other tools.
        </p>
        <p class="data-products__action">
          <a href="#">See how</a>
        </p>
      </article>
      <article class="data-products__product">
        <h3 class="gamma">Embed vote results</h3>
        <p>
          Embed the results of a single vote on your website using our
          visualization templates.
        </p>
        <p class="data-products__action">
          <a href="#">See how</a>
        </p>
      </article>
    </div>
  );
}

export default DataProducts;
