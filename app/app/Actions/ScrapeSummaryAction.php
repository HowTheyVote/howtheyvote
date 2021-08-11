<?php

namespace App\Actions;

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
        $summaryId = $this->scrapeAction->execute('summary_id', [
            'reference' => $voteCollection->reference,
        ]);

        if (! $summaryId) {
            return;
        }

        $text = $this->scrapeAction->execute('summary', [
            'summary_id' => $summaryId,
        ]);

        $summary = Summary::query()
            ->where('reference', $voteCollection->reference)
            ->firstOrNew();

        $summary->reference = $voteCollection->reference;
        $summary->oeil_id = $summaryId;
        $summary->text = $text;

        $summary->save();
    }
}
