<?php

namespace App\Http\Controllers;

use App\GroupMembership;
use App\Member;
use Illuminate\Support\Carbon;
use Spatie\SimpleExcel\SimpleExcelWriter;

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

    // TODO: paramtetrize
    public function csv()
    {
        $date = Carbon::now();
        $rows = Member::activeAt($date)->get()->map(function ($member) {
            $group = GroupMembership::query()
                ->with('group')
                ->where('member_id', $member->id)
                ->activeAt(Carbon::now())
                ->first()
                ->group ?? null;

            return [
                'member_id' => $member->id,
                'first_name' => $member->first_name,
                'last_name' => $member->last_name,
                'birthday' => $member->date_of_birth,
                'email' => $member->email,
                'twitter' => $member->twitter,
                'facebook' => $member->facebook,
                'first_name' => $member->first_name,
                'group.abbreviation' => $group->abbreviation,
                'group.name' => $group->name,
                'country.code' => $member->country->value,
                'country.name' => $member->country->label,
            ];
        })->toArray();

        ob_start();
        $writer = SimpleExcelWriter::createWithoutBom('php://output', 'csv');
        $writer->addRows($rows)->close();
        $csv = ob_get_clean();

        return response($csv, 200, ['Content-Type' => 'text/csv']);
    }
}
