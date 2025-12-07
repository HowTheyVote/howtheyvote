type CopyrightLinkProps = {
  content: string;
  sourceUrl: string;
} & (
  | { startYear: number; endYear: number; year?: never }
  | { startYear?: never; endYear?: never; year: number }
);

function CopyrightLink({
  content,
  sourceUrl,
  startYear,
  endYear,
  year,
}: CopyrightLinkProps) {
  return (
    <>
      {content}
      {": © European Union "}
      {year ? year : `${startYear}–${endYear}`}
      {" · "}
      <a rel="noopener noreferrer" target="_blank" href={sourceUrl}>
        Source: EP
      </a>
    </>
  );
}

export default CopyrightLink;
