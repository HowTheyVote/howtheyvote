import type { Country, Group, Member, MemberVote, NationalParty } from "../api";

export type SerializedMemberVotes = {
  items: Array<
    [
      number,
      string,
      string,
      Group["code"] | undefined,
      NationalParty["id"] | undefined,
      Country["code"],
      MemberVote["position"],
    ]
  >;
  groups: Partial<Record<Group["code"], Group>>;
  countries: Partial<Record<Country["code"], Country>>;
  national_parties: Partial<Record<NationalParty["id"], NationalParty>>;
};

export function serializeMemberVotes(
  memberVotes: Array<MemberVote>,
): SerializedMemberVotes {
  const serialized: SerializedMemberVotes = {
    items: [],
    groups: {},
    countries: {},
    national_parties: {},
  };

  for (const { member, position } of memberVotes) {
    serialized.items.push([
      member.id,
      member.full_name,
      member.thumb_url,
      member?.group?.code,
      member?.national_party?.id,
      member.country.code,
      position,
    ]);

    if (member.group) {
      serialized.groups[member.group.code] = member.group;
    }

    if (member.national_party) {
      serialized.national_parties[member.national_party.id] =
        member.national_party;
    }

    serialized.countries[member.country.code] = member.country;
  }

  return serialized;
}

export function deserializeMemberVotes({
  items,
  groups,
  countries,
  national_parties,
}: SerializedMemberVotes): Array<MemberVote> {
  const deserialized: Array<MemberVote> = [];

  for (const item of items) {
    const [
      id,
      full_name,
      thumb_url,
      group_code,
      national_party_id,
      country_code,
      position,
    ] = item;

    const group = group_code ? groups[group_code] : undefined;
    const country = countries[country_code] as Country;
    const national_party = national_party_id
      ? national_parties[national_party_id]
      : undefined;

    deserialized.push({
      member: {
        id,
        full_name,
        thumb_url,
        group,
        country,
        national_party,
      } as Member,
      position: position,
    });
  }

  return deserialized;
}
