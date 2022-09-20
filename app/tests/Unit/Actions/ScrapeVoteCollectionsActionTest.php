<?php

use App\Actions\ScrapeVoteCollectionsAction;
use App\Enums\VoteTypeEnum;
use App\Session;
use App\Summary;
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
    Http::fakeJsonFromFile('*/vote_collections?term=9&date=2021-10-19', 'vote_collections-no-reference.json');
    Http::fakeJsonFromFile('*/summary_id?reference=A9-0019%2F2021&week_of_year=10', 'summary_id.json');
    Http::fakeJsonFromFile('*/summary?summary_id=1234567', 'summary.json');
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
    expect($vote->formatted)->toEqual('§ 13/1');
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

it('scrapes summary for reference', function () {
    $this->action->execute($this->term, $this->date);
    $voteCollection = VoteCollection::first();

    expect($voteCollection->summary->reference)->toBe('A9-0019/2021');
});

it('does not scrape summary if there is no reference', function () {
    $this->action->execute($this->term, new Carbon('2021-10-19'));
    $voteCollection = VoteCollection::first();

    expect($voteCollection->summary)->toBe(null);
});

it('does not scrape summary if summary exists', function () {
    Summary::factory([
        'reference' => 'A9-0019/2021',
        'text' => 'This summary already exists',
    ])->create();

    $this->action->execute($this->term, $this->date);
    $voteCollection = VoteCollection::first();

    expect(Summary::count())->toEqual(1);
    expect($voteCollection->summary->text)->toEqual('This summary already exists');
});

it('references correct session in created votes', function () {
    $session = Session::factory([
        'start_date' => '2021-03-06',
        'end_date' => '2021-03-09',
        'id' => 1,
    ])->create();

    $this->action->execute($this->term, $this->date);

    expect(Vote::first()->session_id)->toEqual(1);
});
