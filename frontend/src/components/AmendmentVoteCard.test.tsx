import { describe, it } from "node:test";
import { render, screen } from "@testing-library/preact";
import type { RelatedVote } from "../api";
import AmendmentVoteCard from "./AmendmentVoteCard";

describe("AmendmentVoteCard", () => {
  it("handles votes without amendment information", () => {
    const vote = {
      id: 179617,
      display_title: "Second World Summit for Social Development",
      description: "Proposition de résolution (ensemble du texte)",
      is_main: true,
      timestamp: "2025-10-09T00:00:00+00:00",
      result: "ADOPTED",
    } as RelatedVote;

    render(<AmendmentVoteCard vote={vote} />);

    screen.getByRole("heading", {
      name: "Proposition de résolution (ensemble du texte)",
    });
    screen.getByTitle("adopted");
  });

  it("handles votes with amendment information", () => {
    const vote = {
      id: 179617,
      display_title: "Second World Summit for Social Development",
      description: "§ 1 - Am 4",
      is_main: false,
      timestamp: "2025-10-09T00:00:00+00:00",
      result: "REJECTED",
      amendment_number: "4",
      amendment_subject: "§ 1",
      amendment_authors: [
        {
          type: "GROUP",
          group: {
            code: "PFE",
            label: "Patriots for Europe",
            short_label: "PfE",
          },
        },
      ],
    } as RelatedVote;

    render(<AmendmentVoteCard vote={vote} />);

    screen.getByRole("heading", { name: "Amendment 4 by PfE" });
    screen.getByText("§ 1");
    screen.getByTitle("rejected");
  });

  it("handles votes with multiple amendment authors", () => {
    const vote = {
      id: 164134,
      display_title:
        "Plants obtained by certain new genomic techniques and their food and feed",
      description: "Article 6, § 3, après le point c - Am 253",
      is_main: false,
      timestamp: "2024-02-07T00:00:00+00:00",
      result: "ADOPTED",
      amendment_number: "253",
      amendment_subject: "Article 6, § 3, after point c",
      amendment_authors: [
        {
          type: "GROUP",
          group: {
            code: "SD",
            label: "Progressive Alliance of Socialists and Democrats",
            short_label: "S&D",
          },
        },
        {
          type: "GROUP",
          group: {
            code: "GREEN_EFA",
            label: "Green/European Free Alliance",
            short_label: "Greens/EFA",
          },
        },
      ],
    } as RelatedVote;

    render(<AmendmentVoteCard vote={vote} />);

    screen.getByRole("heading", { name: "Amendment 253 by S&D, Greens/EFA" });
    screen.getByText("Article 6, § 3, after point c");
    screen.getByTitle("adopted");
  });

  it("handles votes with different types of authors", () => {
    const vote = {
      id: 166284,
      display_title: "Weights and dimensions of certain road vehicles",
      description:
        "Article 1, alinéa 1, point 4; Directive 96/53/CE; Article 4 ter - Am 58S= 65S=",
      is_main: false,
      timestamp: "2024-03-12T00:00:00+00:00",
      result: "REJECTED",
      amendment_number: "58D= 65D=",
      amendment_subject:
        "Article 1, § 1, point 4 Directive 96/53/EC; Article 4 b",
      amendment_authors: [
        {
          type: "GROUP",
          group: {
            code: "GREEN_EFA",
            label: "Green/European Free Alliance",
            short_label: "Greens/EFA",
          },
        },
        { type: "MEMBERS" },
      ],
    } as RelatedVote;

    render(<AmendmentVoteCard vote={vote} />);

    screen.getByRole("heading", {
      name: "Amendment 58D= 65D= by Greens/EFA, MEPs",
    });
    screen.getByText("Article 1, § 1, point 4 Directive 96/53/EC; Article 4 b");
    screen.getByTitle("rejected");
  });

  it("handles votes on individual parts of the text", () => {
    const vote = {
      id: 179612,
      display_title: "Second World Summit for Social Development",
      description: "§ 17",
      is_main: false,
      timestamp: "2025-10-09T00:00:00+00:00",
      result: "REJECTED",
      amendment_number: "§",
      amendment_subject: "§ 17",
      amendment_authors: [{ type: "ORIGINAL_TEXT" }],
    } as RelatedVote;

    render(<AmendmentVoteCard vote={vote} />);

    screen.getByRole("heading", { name: "Original text" });
    screen.getByText("§ 17");
    screen.getByTitle("rejected");
  });
});
