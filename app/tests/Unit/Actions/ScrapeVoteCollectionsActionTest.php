<?php

use App\Actions\ScrapeVoteCollectionsAction;
use App\Enums\VoteTypeEnum;
use App\Term;
use App\Vote;
use App\VoteCollection;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Support\Carbon;

uses(Tests\TestCase::class, RefreshDatabase::class);

beforeEach(function () {
    $this->action = $this->app->make(ScrapeVoteCollectionsAction::class);
    $this->term = Term::factory(['number' => 9])->create();
    $this->date = new Carbon('2021-03-08');

    Http::fakeJsonFromFile('*/vote_collections?term=9&date=2021-03-08', 'vote_collections.json');
});

it('creates new vote collection records', function () {
    $this->action->execute($this->term, $this->date);

    expect(VoteCollection::count())->toEqual(1);

    $voteCollection = VoteCollection::first();

    expect($voteCollection->title)->toEqual('A WTO-compatible EU carbon border adjustment mechanism');
    expect($voteCollection->reference)->toEqual('A9-0019/2021');
});

it('creates associated votes', function () {
    $this->action->execute($this->term, $this->date);

    $voteCollection = VoteCollection::first();

    expect($voteCollection->votes()->count())->toEqual(28);

    $vote = $voteCollection->votes()->skip(5)->first();

    expect($vote->subject)->toEqual('§ 13');
    expect($vote->author)->toEqual('original text');
    expect($vote->type)->toEqual(VoteTypeEnum::SEPARATE());
    expect($vote->amendment)->toEqual(null);
    expect($vote->split_part)->toEqual(1);
});

it('updates existing voting list record', function () {
    $voteCollection = VoteCollection::factory([
        'title' => 'A WTO-compatible EU carbon border adjustment mechanism',
        'reference' => 'Old reference',
        'date' => $this->date,
        'term_id' => $this->term->id,
    ])->create();

    $this->action->execute($this->term, $this->date);

    expect(VoteCollection::count())->toEqual(1);
});

it('does not create duplicate votes when scraping voting list multiple times', function () {
    $this->action->execute($this->term, $this->date);
    $this->action->execute($this->term, $this->date);

    $voteCollection = VoteCollection::first();

    expect(Vote::count())->toEqual(28);
});
