<?php

namespace App\Actions;

use App\Document;

class ScrapeAndSaveDocumentInfoAction
{
    private $scrapeAction;

    public function __construct(ScrapeAction $scrapeAction)
    {
        $this->scrapeAction = $scrapeAction;
    }

    public function execute(Document $document): void
    {
        $data = $this->scrapeAction->execute('document', [
            'type' => $document->type,
            'term' => $document->term->number,
            'number' => $document->number,
            'year' => $document->year,
        ]);

        $document->update([
            'title' => $data['title'],
        ]);
    }
}
