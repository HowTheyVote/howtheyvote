<?php

use App\Actions\ScrapeAndSaveDocumentInfoAction;
use App\Document;
use App\Enums\DocumentTypeEnum;
use App\Term;
use Illuminate\Foundation\Testing\RefreshDatabase;

uses(Tests\TestCase::class, RefreshDatabase::class);

it('updates document data', function () {
    $this->action = $this->app->make(ScrapeAndSaveDocumentInfoAction::class);

    $this->document = Document::factory([
        'type' => DocumentTypeEnum::B(),
        'term_id' => Term::factory(['number' => 9]),
        'number' => 159,
        'year' => 2019,
    ])->create();

    $url = '*/document_info?type=B&term=9&number=159&year=2019';
    Http::fakeJsonFromFile($url, 'document.json');

    $this->action->execute($this->document);

    $title = $this->document->fresh()->title;
    $expected = 'MOTION FOR A RESOLUTION on search and rescue in the Mediterranean';

    expect($title)->toEqual($expected);
});
