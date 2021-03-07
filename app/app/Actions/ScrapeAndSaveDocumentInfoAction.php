<?php

namespace App\Actions;

use App\Document;

class ScrapeAndSaveDocumentInfoAction extends Action
{
    private $scrapeAction;

    public function __construct(ScrapeAction $scrapeAction, ScrapeAndSaveProcedureAction $scrapeProcedureAction)
    {
        $this->scrapeAction = $scrapeAction;
        $this->scrapeProcedureAction = $scrapeProcedureAction;
    }

    public function execute(Document $document): void
    {
        $data = $this->scrapeAction->execute('document_info', [
            'type' => $document->type,
            'term' => $document->term->number,
            'number' => $document->number,
            'year' => $document->year,
        ]);

        $this->log('Importing document info', array_merge(
            $document->toArray(),
            ['title' => $data['title']],
        ));

        $procedure = $document->procedure()->first();

        if (! $procedure) {
            $procedure = $this->scrapeProcedureAction->execute($document);
        }

        $document->update([
            'title' => $data['title'],
            'procedure_id' => $procedure->id,
        ]);
    }
}
