import type { RelatedVote } from "../api";
import Card from "./Card";
import Thumb from "./Thumb";

type AmendmentVoteCardProps = {
  vote: RelatedVote;
};

export default function AmendmentVoteCard({ vote }: AmendmentVoteCardProps) {
  let title = vote.description;
  let meta = null;

  if (
    vote.amendment_number &&
    vote.amendment_subject &&
    vote.amendment_authors
  ) {
    title = `Amendment ${vote.amendment_number}`;
    meta = vote.amendment_subject;

    if (
      vote.amendment_authors.length === 1 &&
      vote.amendment_authors[0].type === "ORIGINAL_TEXT"
    ) {
      title = "Original text";
    } else {
      const authors = vote.amendment_authors
        .map((author): string | null => {
          if (author.type === "GROUP") {
            return author.group?.short_label || "political group";
          }

          if (author.type === "COMMITTEE") {
            return author.committee
              ? `${author.committee.abbreviation} committee`
              : "committee";
          }

          if (author.type === "RAPPORTEUR") {
            return "rapporteur";
          }

          if (author.type === "MEMBERS") {
            return "MEPs";
          }

          // Ignoring types `ORIGNAL_TEXT` and `ORALLY`. The former is handled above,
          // and the latter seems to be super rate: I found only one ocurrence which
          // was an oral amendment for a split vote, that would also be covered by the
          // `ORIGINAL_TEXT` case, though we might need to reconsider this later.

          return null;
        })
        .filter(Boolean);

      if (authors.length > 0) {
        title += ` by ${authors.join(", ")}`;
      }
    }
  }

  return (
    <Card
      title={title}
      meta={meta}
      link={`/votes/${vote.id}`}
      thumb={vote.result && <Thumb style="circle" result={vote.result} />}
    />
  );
}
