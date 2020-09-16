<?php

namespace App\Actions;

use App\Member;
use App\Term;

class ScrapeAndSaveMembersAction
{
    private $scrapeAction;

    public function __construct(ScrapeAction $scrapeAction)
    {
        $this->scrapeAction = $scrapeAction;
    }

    public function execute(Term $term): void
    {
        $response = $this->scrapeAction->execute('members', [
            'term' => $term->number,
        ]);

        foreach ($response as $data) {
            $this->createOrMergeMember($data);
        }
    }

    protected function createOrMergeMember(array $data): Member
    {
        $terms = Term::whereIn('number', $data['terms'])->first();
        $member = Member::firstOrCreate([
            'web_id' => $data['web_id'],
        ]);

        $member->mergeTerms($terms)->save();

        return $member;
    }
}
