<?php

use App\Vote;
use App\VoteCollection;
use Illuminate\Foundation\Testing\RefreshDatabase;

uses(Tests\TestCase::class, RefreshDatabase::class);

it('has a display title', function () {
    $vote = Vote::factory([
        'vote_collection_id' => VoteCollection::factory([
            'title' => 'A nice title',
        ]),
    ])->make();

    expect($vote->display_title)->toEqual('A nice title');
});
