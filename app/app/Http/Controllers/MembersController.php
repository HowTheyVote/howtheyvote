<?php

namespace App\Http\Controllers;

use App\GroupMembership;
use App\Member;
use Illuminate\Support\Carbon;

class MembersController extends Controller
{
    public function show(Member $member)
    {
        return view('members.show', [
            'member' => $member,
            'group' => GroupMembership::query()
                ->with('group')
                ->where('member_id', $member->id)
                ->activeAt(Carbon::now())
                ->first()
                ->group ?? null,

            'votingLists' => $member->
                votingLists()
                ->final()
                ->matched()
                ->orderByDesc('date')
                ->get(),
        ]);
    }
}
