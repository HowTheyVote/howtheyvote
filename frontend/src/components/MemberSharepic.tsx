import type { Member } from "../api";
import Sharepic from "./Sharepic";

import "./MemberSharepic.css";

type MemberSharepicProps = {
  member: Member;
};

export default function MemberSharepic({ member }: MemberSharepicProps) {
  return (
    <Sharepic>
      <div class="member-sharepic">
        <img class="member-sharepic__photo" src={member.photo_url} alt="" />
        <div>
          <h1 class="beta member-sharepic__title">
            {member.first_name} {member.last_name}
          </h1>
          <p class="member-sharepic__subtitle">
            Find out how Members of the European Parliament vote.
          </p>
          <p>
            <strong>On HowTheyVote.eu.</strong>
          </p>
        </div>
      </div>
    </Sharepic>
  );
}
