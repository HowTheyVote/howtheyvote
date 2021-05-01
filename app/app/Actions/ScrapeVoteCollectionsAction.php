<?php

namespace App\Actions;

use App\Term;
use App\VoteCollection;
use Illuminate\Support\Carbon;

class ScrapeVoteCollectionsAction extends Action
{
    private $scrapeAction;

    public function __construct(ScrapeAction $scrapeAction)
    {
        $this->scrapeAction = $scrapeAction;
    }

    public function execute(Term $term, Carbon $date): void
    {
        $response = $this->scrapeAction->execute('vote_collections', [
            'term' => $term->number,
            'date' => $date->toDateString(),
        ]);

        $total = count($response);

        foreach ($response as $key => $data) {
            $current = $key + 1;

            $this->log("Importing vote collection {$current} of {$total}", [
                'title' => $data['title'],
            ]);

            $voteCollection = $this->createOrUpdateVoteCollection($term, $date, $data);
        }

        $this->log("Imported {$total} vote collections for {$date}");
    }

    private function createOrUpdateVoteCollection(Term $term, Carbon $date, array $data) : VoteCollection
    {
        $voteCollection = VoteCollection::firstOrNew([
            'title' => $data['title'],
            'date' => $date,
            'term_id' => $term->id,
        ]);

        $voteCollection->fill([
            'reference' => $data['reference'],
        ]);

        $voteCollection->save();

        return $voteCollection;
    }
}
