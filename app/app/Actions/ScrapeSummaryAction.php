<?php

namespace App\Actions;

use App\Exceptions\ScrapingException;
use App\Summary;
use App\VoteCollection;

class ScrapeSummaryAction extends Action
{
    private $scrapeAction;

    public function __construct(ScrapeAction $scrapeAction)
    {
        $this->scrapeAction = $scrapeAction;
    }

    public function execute(VoteCollection $voteCollection): void
    {
        try {
            $summaryId = $this->scrapeAction->execute('summary_id', [
                'reference' => $voteCollection->reference,
                'week_of_year' => $voteCollection->date->isoWeek(),
            ]);

            $text = $this->scrapeAction->execute('summary', [
                'summary_id' => $summaryId,
            ]);
        } catch (ScrapingException $exception) {
            report($exception);

            return;
        }

        $summary = Summary::query()
            ->where('reference', $voteCollection->reference)
            ->firstOrNew();

        $summary->reference = $voteCollection->reference;
        $summary->oeil_id = $summaryId;
        $summary->text = $text;

        $summary->save();
    }
}
