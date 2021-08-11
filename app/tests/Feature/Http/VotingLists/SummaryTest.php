<?php

use App\Summary;
use App\Vote;
use App\VoteCollection;
use App\VotingList;
use Illuminate\Foundation\Testing\RefreshDatabase;

uses(Tests\TestCase::class, RefreshDatabase::class);

beforeEach(function () {
    $this->votingList = VotingList::factory([
        'vote_id' => Vote::factory([
            'vote_collection_id' => VoteCollection::factory([
                'reference' => 'A9-1234/2021',
            ]),
        ]),
    ])->create();
});

it('returns 404 if summary does not exist', function () {
    $response = $this->get("/votes/{$this->votingList->id}/summary");
    expect($response)->toHaveStatus(404);
})->only();

it('renders successfully if summary exists', function () {
    Summary::factory([
        'reference' => 'A9-1234/2021',
        'text' => 'Summary for A9-1234/2021',
    ])->create();

    $response = $this->get("/votes/{$this->votingList->id}/summary");

    expect($response)->toHaveStatus(200);
    expect($response)->toSee('Summary for A9-1234/2021');
});
