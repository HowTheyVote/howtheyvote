<?php

namespace App\Actions;

use App\Enums\VoteResultEnum;
use App\Enums\VoteTypeEnum;
use App\Exceptions\ScrapingException;
use App\Session;
use App\Term;
use App\Vote;
use App\VoteCollection;
use Illuminate\Support\Carbon;

class ScrapeVoteCollectionsAction extends Action
{
    private $scrapeAction;

    private $summaryAction;

    public function __construct(ScrapeAction $scrapeAction, ScrapeSummaryAction $summaryAction)
    {
        $this->scrapeAction = $scrapeAction;
        $this->summaryAction = $summaryAction;
    }

    public function execute(Term $term, Carbon $date): void
    {
        try {
            $response = $this->scrapeAction->execute('vote_collections', [
                'term' => $term->number,
                'date' => $date->toDateString(),
            ]);
        } catch (ScrapingException $exception) {
            report($exception);

            return;
        }

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

    private function createOrUpdateVoteCollection(Term $term, Carbon $date, array $data): VoteCollection
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

        $this->createSummary($voteCollection);

        if (! $voteCollection->wasRecentlyCreated) {
            $voteCollection->votes()->delete();
        }

        $session = Session::where('start_date', '<=', $date)
            ->where('end_date', '>=', $date)->first();

        foreach ($data['votes'] as $vote) {
            Vote::create([
                'author' => $vote['author'],
                'subject' => $vote['subject'],
                'type' => VoteTypeEnum::make($vote['type']),
                'result' => VoteResultEnum::make($vote['result']),
                'split_part' => $vote['split_part'],
                'amendment' => $vote['amendment'],
                'vote_collection_id' => $voteCollection->id,
                'formatted' => $vote['formatted'],
                'remarks' => $vote['remarks'],
                'reference' => $vote['reference'],
                'subheading' => $vote['subheading'],
                'session_id' => $session?->id,
                'final' => $vote['final'],
            ]);
        }

        return $voteCollection;
    }

    private function createSummary(VoteCollection $voteCollection): void
    {
        if (! $voteCollection->summary && $voteCollection->reference) {
            $this->summaryAction->execute($voteCollection);
        }
    }
}
