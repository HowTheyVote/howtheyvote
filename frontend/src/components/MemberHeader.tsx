import type { Member } from "../api";
import Wrapper from "./Wrapper";

import "./MemberHeader.css";

type MemberHeaderProps = {
  member: Member;
};

export default function MemberHeader({ member }: MemberHeaderProps) {
  return (
    <header className="member-header">
      <Wrapper className="member-header__wrapper">
        <img class="member-header__photo" src={member.photo_url} alt="" />
        <div class="member-header__text">
          <h1 class="member-header__title alpha">
            {member.first_name} {member.last_name}
          </h1>
          <p class="member-header__subtitle">
            {member.country.label}
            {member.group && ` · ${member.group.label}`}
          </p>
        </div>
      </Wrapper>
    </header>
  );
}
