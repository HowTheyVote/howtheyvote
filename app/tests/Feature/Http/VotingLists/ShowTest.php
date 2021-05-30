<?php

use App\Enums\CountryEnum;
use App\Enums\VoteResultEnum;
use App\Group;
use App\Member;
use App\Vote;
use App\VoteCollection;
use App\VotingList;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Support\Carbon;

uses(Tests\TestCase::class, RefreshDatabase::class);

beforeEach(function () {
    $date = new Carbon('2021-05-23');

    $greens = Group::factory([
        'code' => 'GREENS',
        'abbreviation' => 'Greens/EFA',
    ])->create();

    $greensFor = Member::factory([
        'first_name' => 'Jane',
        'last_name' => 'DOE',
        'country' => CountryEnum::NL(),
    ])->activeAt($date, $greens)->count(1);

    VotingList::factory([
        'id' => 1,
        'description' => 'Matched Voting List',
        'date'=> $date,
        'vote_id' => Vote::factory([
            'result' => VoteResultEnum::ADOPTED(),
            'vote_collection_id' => VoteCollection::factory(['title' => 'My Title']),
        ]),
    ])->withStats()->withMembers('FOR', $greensFor)->create();
});

it('does not fail if there is no associated vote', function () {
    $votingList = VotingList::factory([
        'id' => 10,
        'vote_id' => null,
        'description' => 'Unmatched Voting List',
    ])->withStats()->create();

    $response = $this->get('/votes/10');
    expect($response)->toHaveStatus(200);
});

it('shows a title', function () {
    $response = $this->get('/votes/1');
    expect($response)->toHaveSelectorWithText('h1', 'My Title');
});

it('shows the result of the vote', function () {
    $response = $this->get('/votes/1');
    expect($response)->toHaveSelectorWithText('h1 + p', 'adopted');
    expect($response)->toHaveSelector('h1 + p > .thumb--adopted.thumb--circle');
});

it('displays a bar chart', function () {
    $response = $this->get('/votes/1');
    expect($response)->toHaveSelector('.vote-result-chart');
});

it('shows a list of members', function () {
    $response = $this->get('/votes/1');

    expect($response)->toHaveSelectorWithText('.list-item__text', 'Jane DOE');
    expect($response)->toHaveSelectorWithText('.list-item__text', 'Greens/EFA · Netherlands');
    expect($response)->toHaveSelector('.thumb--for.thumb--circle.list-item__thumb');
});
