import "./Pagination.css";

type PaginationProps = {
  next?: string | false;
  prev?: string | false;
};

export default function Pagination({ next, prev }: PaginationProps) {
  return (
    <nav class="pagination">
      {prev && (
        <a href={prev} rel="prev">
          <span aria-hidden="true" class="pagination__arrow">
            ←
          </span>
          &nbsp; Previous page
        </a>
      )}

      {next && (
        <a href={next} rel="next">
          Next page &nbsp;
          <span aria-hidden="true" class="pagination__arrow">
            →
          </span>
        </a>
      )}
    </nav>
  );
}
