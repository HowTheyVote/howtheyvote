<?php

use App\Actions\ScrapeAndSaveVoteResultsAction;
use App\Document;
use App\Enums\DocumentTypeEnum;
use App\Term;
use App\Vote;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Support\Carbon;

uses(Tests\TestCase::class, RefreshDatabase::class);

beforeEach(function () {
    $this->action = $this->app->make(ScrapeAndSaveVoteResultsAction::class);
    $this->term = Term::factory(['number' => 9])->create();
    $this->date = new Carbon('2019-10-24');

    Http::fakeJsonFromFile('*/vote_results?term=9&date=2019-10-24', 'vote_results.json');
});

it('creates new vote record including relations', function () {
    $this->action->execute($this->term, $this->date);

    expect(Vote::count())->toEqual(1);

    $vote = Arr::except(Vote::first()->getAttributes(), [
        'created_at',
        'updated_at',
        'id',
        'document_id',
    ]);

    expect($vote)->toEqual([
        'doceo_vote_id' => 109619,
        'date' => '2019-10-24 00:00:00',
        'description' => '§ 1/2',
        'term_id' => $this->term->id,
    ]);

    expect(Vote::first()->document)->not()->toBeNull();
});

it('creates new related document records', function () {
    $this->action->execute($this->term, $this->date);

    expect(Document::count())->toEqual(1);

    $document = Arr::except(Document::first()->getAttributes(), [
        'created_at',
        'updated_at',
        'id',
    ]);

    expect($document)->toEqual([
        'type' => DocumentTypeEnum::B(),
        'term_id' => $this->term->id,
        'number' => 154,
        'year' => 2019,
        'title' => null,
    ]);
});

it('finds and relates existing document record', function () {
    $document = Document::create([
        'type' => DocumentTypeEnum::B(),
        'term_id' => $this->term->id,
        'number' => 154,
        'year' => 2019,
        'title' => 'MOTION FOR A RESOLUTION on search and rescue in the Mediterranean',
    ]);

    $this->action->execute($this->term, $this->date);

    expect(Document::count())->toEqual(1);
    expect(Vote::first()->document_id)->toEqual($document->id);
});
