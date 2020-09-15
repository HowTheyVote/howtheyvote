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

    public function execute(Member $member): void
    {
        $data = $this->scrapeAction->execute('member_info', [
            'web_id' => $member->web_id,
        ]);

        $data['country_id'] = Country::whereCode($data['country'])->first()->id;

        $member->update($data);
    }
}
