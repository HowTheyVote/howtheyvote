<?php

namespace App\Actions;

use App\Country;
use App\Member;

class ScrapeAndSaveMemberInfoAction
{
    private $scrapeAction;

    public function __construct(ScrapeAction $scrapeAction)
    {
        $this->scrapeAction = $scrapeAction;
    }

    public function execute(int $webId): Member
    {
        $member = Member::whereWebId($webId)->first();

        $data = $this->scrapeAction->execute('member_info', ['web_id' => $webId]);
        $data['country_id'] = Country::whereCode($data['country'])->first()->id;

        $member->update($data);

        return $member;
    }
}
