<?php

namespace App\Actions;

use App\Group;
use App\GroupMembership;
use App\Member;
use App\Term;

class ScrapeAndSaveMemberGroupsAction extends Action
{
    private $scrapeAction;

    public function __construct(ScrapeAction $scrapeAction)
    {
        $this->scrapeAction = $scrapeAction;
    }

    public function execute(Member $member, Term $term): void
    {
        $response = $this->scrapeAction->execute('member_groups', [
            'web_id' => $member->web_id,
            'term' => $term->number,
        ]);

        $total = count($response);

        foreach ($response as $key => $data) {
            $current = $key + 1;
            $this->log("Importing group membership {$key} of {$total}", $data);

            $this->createOrUpdateMembership($member, $term, $data);
        }
    }

    public function createOrUpdateMembership(Member $member, Term $term, array $data): GroupMembership
    {
        $group = Group::whereCode($data['group'])->first();

        $data = [
            'member_id' => $member->id,
            'group_id' => $group->id,
            'term_id' => $term->id,
            'start_date' => $data['start_date'],
            'end_date' => $data['end_date'],
        ];

        $membership = GroupMembership::where([
            'member_id' => $data['member_id'],
            'start_date' => $data['start_date'],
        ])->first();

        if (! $membership) {
            return GroupMembership::create($data);
        }

        $membership->update($data);

        return $membership;
    }
}
