<?php

namespace App\Http\Controllers;

use App\Member;
use Illuminate\Support\Carbon;

class MembersController extends Controller
{
    public function show(Member $member)
    {
        $lastGroupMembership = $member->lastGroupMembership();
        $lastActive = ($lastGroupMembership->end_date !== null) ? Carbon::parse($lastGroupMembership->end_date)->format('F Y') : null;

        return view('members.show', [
            'member' => $member,
            'group' => $lastGroupMembership->group,
            'lastActive' => $lastActive,
        ]);
    }
}
