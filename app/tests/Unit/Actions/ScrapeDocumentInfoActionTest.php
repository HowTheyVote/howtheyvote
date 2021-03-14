<?php

use App\Actions\ScrapeDocumentInfoAction;
use App\Document;
use App\Enums\DocumentTypeEnum;
use App\Procedure;
use App\Term;
use Illuminate\Foundation\Testing\RefreshDatabase;

uses(Tests\TestCase::class, RefreshDatabase::class);

beforeEach(function () {
    //TODO: use dep injection to mock actions
    Http::fakeJsonFromFile('*/procedure?type=B&term=9&number=159&year=2019', 'procedure.json');
    Http::fakeJsonFromFile('*/document_info?type=B&term=9&number=159&year=2019', 'document_info.json');

    $this->document = Document::factory([
        'type' => DocumentTypeEnum::B(),
        'term_id' => Term::factory(['number' => 9]),
        'number' => 159,
        'year' => 2019,
    ])->create();
});

it('updates document data', function () {
    $this->action = $this->app->make(ScrapeDocumentInfoAction::class);
    $this->action->execute($this->document);

    $title = $this->document->fresh()->title;
    $expected = 'MOTION FOR A RESOLUTION on search and rescue in the Mediterranean';

    expect($title)->toEqual($expected);
});

it('creates related procedure record', function () {
    $this->action = $this->app->make(ScrapeDocumentInfoAction::class);
    $this->action->execute($this->document);

    expect(Procedure::count())->toEqual(1);

    $procedure = $this->document->fresh()->procedure_id;
    $expected = Procedure::first()->id;

    expect($procedure)->toEqual($expected);
});
