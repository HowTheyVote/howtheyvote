import type { Country, Group, Member, MemberVote } from "../api";

export type SerializedMemberVotes = {
  items: Array<
    [
      number,
      string,
      string,
      string,
      string,
      Group["code"] | undefined,
      Country["code"],
      MemberVote["position"],
    ]
  >;
  groups: Partial<Record<Group["code"], Group>>;
  countries: Partial<Record<Country["code"], Country>>;
};

export function serializeMemberVotes(
  memberVotes: Array<MemberVote>,
): SerializedMemberVotes {
  const serialized: SerializedMemberVotes = {
    items: [],
    groups: {},
    countries: {},
  };

  for (const { member, position } of memberVotes) {
    serialized.items.push([
      member.id,
      member.first_name,
      member.last_name,
      member.full_name,
      member.thumb_url,
      member?.group?.code,
      member.country.code,
      position,
    ]);

    if (member.group) {
      serialized.groups[member.group.code] = member.group;
    }

    serialized.countries[member.country.code] = member.country;
  }

  return serialized;
}

export function deserializeMemberVotes({
  items,
  groups,
  countries,
}: SerializedMemberVotes): Array<MemberVote> {
  const deserialized: Array<MemberVote> = [];

  for (const item of items) {
    const [
      id,
      first_name,
      last_name,
      full_name,
      thumb_url,
      group_code,
      country_code,
      position,
    ] = item;

    const group = group_code ? groups[group_code] : undefined;
    const country = countries[country_code] as Country;

    deserialized.push({
      member: {
        id,
        first_name,
        last_name,
        full_name,
        thumb_url,
        group,
        country,
      } as Member,
      position: position,
    });
  }

  return deserialized;
}
