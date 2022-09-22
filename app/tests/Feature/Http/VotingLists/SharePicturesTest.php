<?php

use App\Enums\VoteResultEnum;
use App\Vote;
use App\VotingList;
use Illuminate\Foundation\Testing\RefreshDatabase;

uses(Tests\TestCase::class, RefreshDatabase::class);

it('renders successfully', function () {
    $votingList = VotingList::factory()->withStats()->create();
    $response = $this->get("/votes/{$votingList->id}/share-picture");

    expect($response)->toHaveStatus(200);
});

it('shows the result of the vote', function () {
    $votingList = VotingList::factory([
        'vote_id' => Vote::factory([
            'result' => VoteResultEnum::REJECTED,
        ]),
    ])->withStats()->create();

    $response = $this->get("/votes/{$votingList->id}/share-picture");

    expect($response)->toHaveSelector('.thumb--circle');
});
