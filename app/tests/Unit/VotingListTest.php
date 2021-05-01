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
