<?php

use App\Enums\VoteResultEnum;
use App\Vote;
use App\VoteCollection;
use App\VotingList;
use Illuminate\Foundation\Testing\RefreshDatabase;

uses(Tests\TestCase::class, RefreshDatabase::class);

beforeEach(function () {
    VotingList::factory([
        'id' => 1,
        'description' => 'Matched Voting List',
        'vote_id' => Vote::factory([
            'result' => VoteResultEnum::ADOPTED(),
            'vote_collection_id' => VoteCollection::factory(['title' => 'My Title']),
        ]),
    ])->withStats()->create();
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
    expect($response)->toSeeText('My Title');
});

it('shows the result of the vote', function () {
    $response = $this->get('/votes/1');
    expect($response)->toSee('adopted');
    expect($response)->toSee('thumb--adopted thumb--circle');
});

it('displays a bar chart', function () {
    $response = $this->get('/votes/1');
    expect($response)->toSee('vote-result-chart');
});
