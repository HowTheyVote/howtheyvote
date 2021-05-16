<?php

use App\VotingList;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Vinkla\Hashids\Facades\Hashids;

uses(Tests\TestCase::class, RefreshDatabase::class);

it('has a hash id', function () {
    $votingList = VotingList::factory(['id' => 1])->make();

    $expected = Hashids::encode(1);
    expect($votingList->hash_id)->toEqual($expected);
});

it('has display title based on description', function () {
    $votingList = VotingList::factory([
        'description' => 'Content of the description',
        'vote_id' => null,
    ])->make();

    expect($votingList->display_title)->toEqual('Content of the description');
});

it('has display title based on associated vote title', function () {
    $votingList = VotingList::factory([
        'description' => 'Content of the description',
        'vote' => $this->mock(Vote::class, fn ($mock) => $mock->display_title = 'Blub'),
    ])->make();

    expect($votingList->display_title)->toEqual('Blub');
});
