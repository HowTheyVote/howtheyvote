import { strict as assert } from "node:assert";
import { describe, it } from "node:test";
import { render, within } from "@testing-library/preact";
import userEvent from "@testing-library/user-event";
import type { Group, Member } from "../api";
import MemberVotesList from "./MemberVotesList";

const country = {
  code: "DE" as const,
  label: "Germany",
};

const group = {
  code: "GREENS" as const,
  label: "The Greens/European Free Alliance",
  short_label: "Greens/EFA",
};

const memberVotes = [
  {
    member: {
      id: 1,
      full_name: "Max MUSTERMANN",
      terms: [9],
      country,
      group,
    } as Member,
    position: "FOR" as const,
  },
  {
    member: {
      id: 2,
      full_name: "Beate BEISPIEL",
      terms: [9],
      country,
      group,
    } as Member,
    position: "AGAINST" as const,
  },
  {
    member: {
      id: 3,
      full_name: "Noël TOULEMONDE",
      terms: [9],
      country,
      group,
    } as Member,
    position: "ABSTENTION" as const,
  },
];

describe("MemberVotesList", () => {
  it("renders a list of members and their votes", () => {
    const { getAllByRole } = render(
      <MemberVotesList
        memberVotes={memberVotes}
        groups={[group]}
        countries={[country]}
      />,
    );
    const items = getAllByRole("listitem");

    assert.strictEqual(items.length, 3);
    assert.ok(within(items[0]).getByText("Max MUSTERMANN"));
    assert.ok(within(items[0]).getByText("for"));
    assert.ok(within(items[1]).getByText("Beate BEISPIEL"));
    assert.ok(within(items[1]).getByText("against"));
    assert.ok(within(items[2]).getByText("Noël TOULEMONDE"));
    assert.ok(within(items[2]).getByText("abstention"));
  });

  it("can search members by name", async () => {
    const { getAllByRole, getByRole } = render(
      <MemberVotesList
        memberVotes={memberVotes}
        groups={[group]}
        countries={[country]}
      />,
    );
    const all = getAllByRole("listitem");
    assert.strictEqual(all.length, 3);

    await userEvent.type(getByRole("searchbox"), "muster");

    const filtered = getAllByRole("listitem");
    assert.strictEqual(filtered.length, 1);
    assert.ok(within(filtered[0]).getByText("Max MUSTERMANN"));
  });

  it("can search members by name with superfluous whitespace", async () => {
    const { getAllByRole, getByRole } = render(
      <MemberVotesList
        memberVotes={memberVotes}
        groups={[group]}
        countries={[country]}
      />,
    );
    const all = getAllByRole("listitem");
    assert.strictEqual(all.length, 3);

    const searchbox = getByRole("searchbox");

    // duplicate whitespace between name and surname
    await userEvent.type(searchbox, "max  muster");

    let filtered = getAllByRole("listitem");
    assert.strictEqual(filtered.length, 1);
    assert.ok(within(filtered[0]).getByText("Max MUSTERMANN"));

    // leading whitespace
    await userEvent.clear(searchbox);
    await userEvent.type(searchbox, " max muster");

    filtered = getAllByRole("listitem");
    assert.strictEqual(filtered.length, 1);
    assert.ok(within(filtered[0]).getByText("Max MUSTERMANN"));
  });

  it("supports basic fuzzy search", async () => {
    const { getAllByRole, getByRole } = render(
      <MemberVotesList
        memberVotes={memberVotes}
        groups={[group]}
        countries={[country]}
      />,
    );
    const all = getAllByRole("listitem");
    assert.strictEqual(all.length, 3);

    await userEvent.type(getByRole("searchbox"), "noel");

    const filtered = getAllByRole("listitem");
    assert.strictEqual(filtered.length, 1);
    assert.ok(within(filtered[0]).getByText("Noël TOULEMONDE"));
  });

  it("can be expanded and collapsed", async () => {
    const memberVotes = [...Array(20).keys()].map((i) => ({
      member: {
        id: i,
        full_name: `Member ${i + 1}`,

        country,
        group,
      } as Member,
      position: "FOR" as const,
    }));

    const { getAllByRole, getByRole } = render(
      <MemberVotesList
        memberVotes={memberVotes}
        groups={[group]}
        countries={[country]}
      />,
    );
    let items = getAllByRole("listitem");

    assert.strictEqual(items.length, 10);
    assert.ok(within(items[0]).getByText("Member 1"));
    assert.ok(within(items[9]).getByText("Member 10"));

    await userEvent.click(getByRole("button", { name: "Show all" }));
    items = getAllByRole("listitem");

    assert.strictEqual(items.length, 20);
    assert.ok(within(items[0]).getByText("Member 1"));
    assert.ok(within(items[19]).getByText("Member 20"));

    assert.ok(getByRole("button", { name: "Show less" }));
  });

  it("filters by political group", async () => {
    const memberVotes = [
      {
        member: {
          id: 1,
          full_name: "Max MUSTERMANN",
          country,
          group: {
            code: "EPP",
            label: "European People’s Party",
          },
        } as Member,
        position: "FOR" as const,
      },
      {
        member: {
          id: 2,
          full_name: "Beate BEISPIEL",
          country,
          group: {
            code: "SD",
            label: "Progressive Alliance of Socialists and Democrats",
          },
        } as Member,
        position: "AGAINST" as const,
      },
    ];

    const groups = memberVotes.map(({ member }) => member.group);

    const { getAllByRole, getByRole } = render(
      <MemberVotesList
        memberVotes={memberVotes}
        groups={groups as Array<Group>}
        countries={[country]}
      />,
    );

    let items = getAllByRole("listitem");
    assert.strictEqual(items.length, 2);

    await userEvent.selectOptions(
      getByRole("combobox", { name: "Filter by political group" }),
      "SD",
    );

    items = getAllByRole("listitem");
    assert.strictEqual(items.length, 1);
    assert.ok(within(items[0]).getByText("Beate BEISPIEL"));
  });

  it("filters by country", async () => {
    const memberVotes = [
      {
        member: {
          id: 1,
          full_name: "Max MUSTERMANN",
          group,
          country: {
            code: "DEU",
            label: "Germany",
          },
        } as Member,
        position: "FOR" as const,
      },
      {
        member: {
          id: 2,
          full_name: "Noël TOULEMONDE",
          group,
          country: {
            code: "FRA",
            label: "France",
          },
        } as Member,
        position: "AGAINST" as const,
      },
    ];

    const countries = memberVotes.map(({ member }) => member.country);

    const { getAllByRole, getByRole } = render(
      <MemberVotesList
        memberVotes={memberVotes}
        groups={[group]}
        countries={countries}
      />,
    );

    let items = getAllByRole("listitem");
    assert.strictEqual(items.length, 2);

    await userEvent.selectOptions(
      getByRole("combobox", { name: "Filter by country" }),
      "FRA",
    );

    items = getAllByRole("listitem");
    assert.strictEqual(items.length, 1);
    assert.ok(within(items[0]).getByText("Noël TOULEMONDE"));
  });

  it("filters by position", async () => {
    const memberVotes = [
      {
        member: {
          id: 1,
          full_name: "Max MUSTERMANN",
          group,
          country,
        } as Member,
        position: "FOR" as const,
      },
      {
        member: {
          id: 2,
          full_name: "Beate BEISPIEL",
          group,
          country,
        } as Member,
        position: "AGAINST" as const,
      },
    ];

    const { getAllByRole, getByRole } = render(
      <MemberVotesList
        memberVotes={memberVotes}
        groups={[group]}
        countries={[country]}
      />,
    );

    let items = getAllByRole("listitem");
    assert.strictEqual(items.length, 2);

    await userEvent.selectOptions(
      getByRole("combobox", { name: "Filter by vote position" }),
      "AGAINST",
    );

    items = getAllByRole("listitem");
    assert.strictEqual(items.length, 1);
    assert.ok(within(items[0]).getByText("Beate BEISPIEL"));
  });
});
