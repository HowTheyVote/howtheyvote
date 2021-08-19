<?php

use App\Actions\ScrapeVotingListsAction;
use App\Enums\VotePositionEnum;
use App\Member;
use App\Term;
use App\VotingList;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Support\Carbon;

uses(Tests\TestCase::class, RefreshDatabase::class);

beforeEach(function () {
    $this->action = $this->app->make(ScrapeVotingListsAction::class);
    $this->term = Term::factory(['number' => 9])->create();
    $this->date = new Carbon('2019-10-24');
});

it('creates new voting list record including relations', function () {
    Http::fakeJsonFromFile('*/voting_lists?term=9&date=2019-10-24', 'voting_lists.json');

    $this->action->execute($this->term, $this->date);

    expect(VotingList::count())->toEqual(1);

    $votingList = VotingList::first();

    expect($votingList->doceo_vote_id)->toEqual(109619);
    expect($votingList->date)->toEqual(new Carbon('2019-10-24'));
    expect($votingList->description)->toEqual('B9-0154/2019 - § 1/2');
    expect($votingList->reference)->toEqual('B9-0154/2019');
    expect($votingList->term->id)->toEqual($this->term->id);
});

it('updates existing voting list record based on doceo_vote_id', function () {
    Http::fakeJsonFromFile('*/voting_lists?term=9&date=2019-10-24', 'voting_lists.json');

    $votingList = VotingList::factory([
        'doceo_vote_id' => 109619,
        'date' => $this->date,
        'term_id' => $this->term->id,
        'description' => 'Old Description',
    ])->create();

    $this->action->execute($this->term, $this->date);

    expect(VotingList::count())->toEqual(1);
});

it('updates existing voting lists based on description and reference if doceo_vote_id is null', function () {
    Http::fakeJsonFromFile('*/voting_lists?term=9&date=2019-10-24', 'voting_lists-7.json');

    $this->action->execute($this->term, $this->date);

    expect(VotingList::count())->toEqual(2);
    expect(VotingList::pluck('description'))->toMatchArray([
        'Lorem Ipsum - Am 1',
        'Lorem Ipsum - Am 2',
    ]);
});

it('finds and relates members with position', function () {
    Http::fakeJsonFromFile('*/voting_lists?term=9&date=2019-10-24', 'voting_lists-2.json');

    $member = Member::factory([
        'first_name' => 'Jane',
        'last_name' => 'Doe',
    ])->activeAt($this->date)->create();

    $this->action->execute($this->term, $this->date);

    $votingList = VotingList::first();

    expect($member->votes()->count())->toEqual(1);
    expect($votingList->members()->count())->toEqual(1);

    $position = $member->votes()->first()->pivot->position;
    expect($position)->toEqual(VotePositionEnum::FOR());
});

it('updates related members', function () {
    Http::fakeJsonFromFile('*/voting_lists?term=9&date=2019-10-24', 'voting_lists-2.json');

    $votingList = VotingList::factory([
        'doceo_vote_id' => 109619,
        'date' => $this->date,
        'term_id' => $this->term->id,
    ])->create();

    $member = Member::factory([
        'first_name' => 'Jane',
        'last_name' => 'Doe',
    ])->activeAt($this->date)->create();

    $votingList->members()->attach($member, [
        'position' => VotePositionEnum::AGAINST(),
    ]);

    $this->action->execute($this->term, $this->date);

    expect($votingList->members()->count())->toEqual(1);

    $position = $votingList->members()->first()->pivot->position;
    $expected = VotePositionEnum::FOR();

    expect($position)->toEqual($expected);
});

it('ignores inactive members', function () {
    Http::fakeJsonFromFile('*/voting_lists?term=9&date=2019-10-24', 'voting_lists-2.json');

    $inactiveMember = Member::factory([
        'first_name' => 'Jane',
        'last_name' => 'Doe',
    ])->create();

    $activeMember = Member::factory([
        'first_name' => 'Jane',
        'last_name' => 'Doe',
    ])->activeAt($this->date)->create();

    $this->action->execute($this->term, $this->date);

    $votingList = VotingList::first();

    expect($votingList->members()->count())->toEqual(1);
    expect($votingList->members()->first()->id)->toEqual($activeMember->id);
});

it('finds members by first and last name if ambiguous', function () {
    Http::fakeJsonFromFile('*/voting_lists?term=9&date=2019-10-24', 'voting_lists-3.json');

    $jane = Member::factory([
        'first_name' => 'Jane',
        'last_name' => 'Doe',
    ])->activeAt($this->date)->create();

    $john = Member::factory([
        'first_name' => 'John',
        'last_name' => 'Doe',
    ])->activeAt($this->date)->create();

    $this->action->execute($this->term, $this->date);

    expect(VotingList::count())->toEqual(1);

    $members = VotingList::first()->members();

    $positionJane = (clone $members)
        ->whereFirstName('Jane')
        ->first()
        ->pivot
        ->position;

    $positionJohn = (clone $members)
        ->whereFirstName('John')
        ->first()
        ->pivot
        ->position;

    expect($members->count())->toEqual(2);
    expect($positionJane)->toEqual(VotePositionEnum::FOR());
    expect($positionJohn)->toEqual(VotePositionEnum::AGAINST());
});

it('finds members using case-insensitive comparisons', function () {
    Http::fakeJsonFromFile('*/voting_lists?term=9&date=2019-10-24', 'voting_lists-2.json');
    Member::factory(['last_name' => 'DOE'])->activeAt($this->date)->create();

    $this->action->execute($this->term, $this->date);

    expect(VotingList::first()->members()->first()->last_name)->toEqual('DOE');
});

it('finds members with special characters in name', function () {
    Http::fakeJsonFromFile('*/voting_lists?term=9&date=2019-10-24', 'voting_lists-4.json');
    Member::factory(['last_name' => 'DOÉ'])->activeAt($this->date)->create();

    $this->action->execute($this->term, $this->date);

    expect(VotingList::first()->members()->first()->last_name)->toEqual('DOÉ');
});

it('compiles vote stats', function () {
    Http::fakeJsonFromFile('*/voting_lists?term=9&date=2019-10-24', 'voting_lists-3.json');

    $jane = Member::factory([
        'first_name' => 'Jane',
        'last_name' => 'Doe',
    ])->activeAt($this->date)->create();

    $john = Member::factory([
        'first_name' => 'John',
        'last_name' => 'Doe',
    ])->activeAt($this->date)->create();

    $this->action->execute($this->term, $this->date);

    expect(VotingList::first()->stats['voted'])->toEqual(2);
});

it('handles members who did not vote', function () {
    Http::fakeJsonFromFile('*/voting_lists?term=9&date=2019-10-24', 'voting_lists-6.json');

    $jane = Member::factory([
        'first_name' => 'Jane',
        'last_name' => 'Doe',
    ])->activeAt($this->date)->create();

    $this->action->execute($this->term, $this->date);

    $position = VotingList::first()->members()->first()->pivot->position;
    expect($position)->toEqual(VotePositionEnum::NOVOTE());
});
