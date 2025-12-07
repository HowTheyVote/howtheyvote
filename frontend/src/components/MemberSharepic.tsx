import type { Member } from "../api";
import Sharepic from "./Sharepic";
import Stack from "./Stack";
import Thumb from "./Thumb";

import "./MemberSharepic.css";

type MemberSharepicProps = {
  member: Member;
};

export default function MemberSharepic({ member }: MemberSharepicProps) {
  return (
    <Sharepic>
      <div class="member-sharepic">
        <div class="member-sharepic__photo">
          <img src={member.photo_url} alt="" />
          <Thumb
            className="member-sharepic__for"
            style="circle"
            position="FOR"
          />
          <Thumb
            className="member-sharepic__against"
            style="circle"
            position="AGAINST"
          />
        </div>
        <Stack space="xxs">
          <p>
            <strong>
              {member.country.label}・{member.group?.short_label}
            </strong>
          </p>
          <h1 class="beta member-sharepic__title">
            {member.first_name} {member.last_name}
          </h1>
          <p>Find out how they vote in the European Parliament.</p>
        </Stack>
      </div>
    </Sharepic>
  );
}
