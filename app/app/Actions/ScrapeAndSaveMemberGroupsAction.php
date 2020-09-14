<?php

namespace App\Actions;

use App\Group;
use App\GroupMembership;
use App\Member;
use App\Term;

class ScrapeAndSaveMemberGroupsAction
{
    private $scrapeAction;

    public function __construct(ScrapeAction $scrapeAction)
    {
        $this->scrapeAction = $scrapeAction;
    }

    public function execute(int $webId, int $term): void
    {
        $member = Member::whereWebId($webId)->first();

        $response = $this->scrapeAction->execute('member_groups', [
            'web_id' => $webId,
            'term' => $term,
        ]);

        foreach ($response as $data) {
            $this->createOrUpdateMembership($member, $term, $data);
        }
    }

    public function createOrUpdateMembership(Member $member, int $term, array $data): GroupMembership
    {
        $group = Group::whereCode($data['group'])->first();
        $term = Term::whereNumber($term)->first();

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
