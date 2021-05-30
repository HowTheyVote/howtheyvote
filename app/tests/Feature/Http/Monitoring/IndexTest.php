<?php

use App\VotingList;
use Illuminate\Foundation\Testing\RefreshDatabase;

uses(Tests\TestCase::class, RefreshDatabase::class);

it('display voting lists without associated vote', function () {
    $votingList = VotingList::factory([
        'id' => 1,
        'vote_id' => null,
        'description' => 'Unmatched Voting List',
    ])->create();

    $response = $this->get('/monitoring');

    expect($response)->toHaveSelectorWithText('li', '1 - Unmatched Voting List');
});
