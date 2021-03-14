<?php

namespace App\Actions;

use App\Document;
use App\Procedure;

class ScrapeProcedureAction extends Action
{
    private $scrapeAction;

    public function __construct(ScrapeAction $scrapeAction)
    {
        $this->scrapeAction = $scrapeAction;
    }

    public function execute(Document $document): Procedure
    {
        if ($document->procedure()->first()) {
            $this->log('Returning existing procedure for', $document->toArray());

            return $document->procedure;
        }

        $data = $this->scrapeAction->execute('procedure', [
            'type' => $document->type->label,
            'term' => $document->term->number,
            'number' => $document->number,
            'year' => $document->year,
        ]);

        $this->log('Creating procedure', $data);

        return Procedure::create(array_merge(
            ['title' => $data['title']],
            $data['reference'],
        ));
    }
}
