<?php

namespace App\Http\Controllers;

use App\Member;
use Illuminate\Support\Carbon;

class MemberController extends Controller
{
    public function show(Member $member)
    {
        $memberWithGroup = $member->withGroupMembershipAt(Carbon::now())->find($member->id);
        if (! $memberWithGroup->id) {
            $memberWithGroup = $member;
        }

        return view('members.show', [
            'member' => $memberWithGroup,
            'votingLists' => $member->votes()
                ->whereHas('vote', fn ($query) => $query->final()->matched())
                ->get(),
        ]);
    }
}
