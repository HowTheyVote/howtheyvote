<?php

namespace App\Actions;

use App\Member;
use App\Term;
use Illuminate\Support\Collection;

class ScrapeAndSaveMembersAction
{
    private $scrapeAction;

    public function __construct(ScrapeAction $scrapeAction)
    {
        $this->scrapeAction = $scrapeAction;
    }

    public function execute(int $term): Collection
    {
        $response = $this->scrapeAction->execute('members', ['term' => $term]);

        return collect($response)->each(function ($data) {
            return $this->createOrMergeMember($data);
        });
    }

    protected function createOrMergeMember(array $data): bool
    {
        $member = Member::whereWebId($data['web_id'])->first();
        $terms = Term::whereIn('number', $data['terms'])->get();

        if (! $member) {
            $member = Member::create(['web_id' => $data['web_id']]);
        }

        return $member->mergeTerms($terms)->save();
    }
}
