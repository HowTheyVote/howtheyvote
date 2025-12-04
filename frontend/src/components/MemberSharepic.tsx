import type { Member } from "../api";
import Sharepic from "./Sharepic";
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
        <div>
          <p style="margin-bottom: 0.5rem">
            <strong>HowTheyVote.eu</strong>
          </p>
          <h1 class="beta member-sharepic__title">
            {member.first_name} {member.last_name}
          </h1>
          <p class="member-sharepic__subtitle">
            Find out how Members of the European Parliament vote.
          </p>
        </div>
      </div>
    </Sharepic>
  );
}
