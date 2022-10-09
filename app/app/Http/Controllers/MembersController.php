<?php

namespace App\Http\Controllers;

use App\Member;
use Illuminate\Support\Carbon;

class MembersController extends Controller
{
    public function show(Member $member)
    {
        return view('members.show', [
            'member' => $member,
            'groupMembershipParameters' => $this->groupMembershipParametersFor($member),
        ]);
    }

    private function groupMembershipParametersFor(Member $member)
    {
        $memberships = Member::find($member->id)->groupMemberships;
        $memberships = $memberships->map(function ($membership) {
            $start = $membership->start_date;
            $end = $membership->end_date;

            // active groupmemberships do not have an end date
            $end = !$end ?  'now' : Carbon::parse($end)->format('F Y');

            $start = Carbon::parse($start)->format('F Y');

            return [
                "name" => $membership->group->name,
                "start" => $start,
                "end" => $end,
            ];
        });
        return $memberships;
    }
}
