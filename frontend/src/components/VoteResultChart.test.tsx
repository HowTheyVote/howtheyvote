import { strict as assert } from "node:assert";
import { describe, it } from "node:test";
import { render, screen } from "@testing-library/preact";
import type { VotePositionCounts } from "../api";
import VoteResultChart from "./VoteResultChart";

const stats: VotePositionCounts = {
  FOR: 5,
  AGAINST: 3,
  ABSTENTION: 2,
  DID_NOT_VOTE: 1,
};

describe("VoteResultChart", () => {
  it("renders the vote result bars", () => {
    render(<VoteResultChart stats={stats} />);
    screen.getByTitle("5 MEPs voted FOR (50%)");
    screen.getByTitle("3 MEPs voted AGAINST (30%)");
    screen.getByTitle("2 MEPs voted ABSTENTION (20%)");
  });

  it("renders the vote summary", () => {
    render(<VoteResultChart stats={stats} />);
    const summary = screen.getByTestId("vote-result-chart-summary");

    assert.strictEqual(
      summary.textContent,
      "For: 5 (50%). Against: 3 (30%). Abstentions: 2 (20%). In total, 10 MEPs voted. 1 MEPs didn’t vote.",
    );
  });
});
