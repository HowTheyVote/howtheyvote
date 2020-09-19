<?php

namespace App\Actions;

use App\Member;
use App\Term;

class ScrapeAndSaveMembersAction extends Action
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

        $total = count($response);

        foreach ($response as $key => $data) {
            $current = $key + 1;
            $this->log("Importing member {$current} of {$total}", $data);

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
