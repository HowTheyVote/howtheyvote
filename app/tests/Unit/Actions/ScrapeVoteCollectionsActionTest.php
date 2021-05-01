<?php

use App\Actions\ScrapeVoteCollectionsAction;
use App\Term;
use App\VoteCollection;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Support\Carbon;

uses(Tests\TestCase::class, RefreshDatabase::class);

beforeEach(function () {
    $this->action = $this->app->make(ScrapeVoteCollectionsAction::class);
    $this->term = Term::factory(['number' => 9])->create();
    $this->date = new Carbon('2021-03-08');
});

it('creates new vote collection records', function () {
    Http::fakeJsonFromFile('*/vote_collections?term=9&date=2021-03-08', 'vote_collections.json');

    $this->action->execute($this->term, $this->date);

    expect(VoteCollection::count())->toEqual(1);

    $voteCollection = VoteCollection::first();

    expect($voteCollection->title)->toEqual('A WTO-compatible EU carbon border adjustment mechanism');
    expect($voteCollection->reference)->toEqual('A9-0019/2021');
});

it('updates existing voting list record', function () {
    Http::fakeJsonFromFile('*/vote_collections?term=9&date=2021-03-08', 'vote_collections.json');

    $voteCollection = VoteCollection::factory([
        'title' => 'A WTO-compatible EU carbon border adjustment mechanism',
        'reference' => 'Old reference',
        'date' => $this->date,
        'term_id' => $this->term->id,
    ])->create();

    $this->action->execute($this->term, $this->date);

    expect(VoteCollection::count())->toEqual(1);
});
