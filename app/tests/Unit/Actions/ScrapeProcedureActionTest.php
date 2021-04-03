<?php

use App\Actions\ScrapeProcedureAction;
use App\Document;
use App\Enums\DocumentTypeEnum;
use App\Enums\ProcedureTypeEnum;
use App\Procedure;
use App\Term;
use Illuminate\Foundation\Testing\RefreshDatabase;

uses(Tests\TestCase::class, RefreshDatabase::class);

beforeEach(function () {
    //TODO: use dep injection to mock actions
    Http::fakeJsonFromFile('*/procedure?type=B&term=9&number=159&year=2019', 'procedure.json');

    $this->document = Document::factory([
        'type' => DocumentTypeEnum::B(),
        'term_id' => Term::factory(['number' => 9]),
        'number' => 159,
        'year' => 2019,
    ])->create();
});

it('scrapes the procedure for a document', function () {
    $this->action = $this->app->make(ScrapeProcedureAction::class);
    $procedure = $this->action->execute($this->document);

    $expected = [
        'title' => 'Search and rescue in the Mediterranean (SAR)',
        'type' => ProcedureTypeEnum::RSP(),
        'number' => 2755,
        'year' => 2019,
        'id' => $procedure->id,
    ];

    expect($procedure->getAttributes())->toEqual($expected);
});

it('does not create duplicates of an already existing procedure', function () {
    $existingProcedure = Procedure::factory([
        'title' => 'Search and rescue in the Mediterranean (SAR)',
        'type' => ProcedureTypeEnum::RSP(),
        'number' => 2755,
        'year' => 2019,
    ])->create();

    $this->document->update(['procedure_id' => $existingProcedure->id]);

    $this->action = $this->app->make(ScrapeProcedureAction::class);
    $procedure = $this->action->execute($this->document);

    expect($procedure->id)->toEqual($existingProcedure->id);
});
