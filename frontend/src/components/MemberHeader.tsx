import type { Member } from "../api";
import Wrapper from "./Wrapper";

import "./MemberHeader.css";
import { bem } from "../lib/bem";

type MemberHeaderProps = {
  member: Member;
  size?: "lg";
};

export default function MemberHeader({ member, size }: MemberHeaderProps) {
  return (
    <header className={bem("member-header", [size])}>
      <Wrapper className="member-header__wrapper">
        <img
          class="member-header__photo"
          src={member.photo_url}
          alt=""
        />
        <div class="member-header__text">
          <h1
            class={`member-header__title ${size === "lg" ? "alpha" : "beta"}`}
          >
            {member.first_name} {member.last_name}
          </h1>
          <p>
            {member.country.label}
            {member.group && ` · ${member.group.label}`}
          </p>
        </div>
      </Wrapper>
    </header>
  );
}
