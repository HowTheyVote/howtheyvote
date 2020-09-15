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
        $member = Member::whereWebId($data['web_id'])->first();
        $terms = Term::whereIn('number', $data['terms'])->get();

        if (! $member) {
            $member = Member::create(['web_id' => $data['web_id']]);
        }

        $member->mergeTerms($terms)->save();

        return $member;
    }
}
