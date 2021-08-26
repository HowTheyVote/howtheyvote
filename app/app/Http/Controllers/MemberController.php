<?php

namespace App\Http\Controllers;

use App\Member;
use Illuminate\Support\Carbon;

class MemberController extends Controller
{
    public function show(Member $member)
    {
        return view('members.show', [
            'member' => $member->withGroupMembershipAt(Carbon::now())->find($member->id),
            'votingLists' => $member->votes()
                ->whereHas('vote', fn ($query) => $query->final()->matched())
                ->get(),
        ]);
    }
}
