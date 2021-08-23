<?php

namespace App\Http\Controllers;

use App\Member;

class MemberController extends Controller
{
    public function show(Member $member)
    {
        return view('members.show', [
            'member' => $member,
            'votes' => $member->votes()
                ->whereHas('vote', fn ($query) => $query->final()->matched())
                ->get(),
        ]);
    }
}
