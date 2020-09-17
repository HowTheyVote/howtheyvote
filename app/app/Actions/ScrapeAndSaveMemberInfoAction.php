<?php

namespace App\Actions;

use App\Enums\CountryEnum;
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

        $data['country'] = CountryEnum::make($data['country']);

        $member->update($data);
    }
}
