<?php

use App\Enums\VoteTypeEnum;
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

it('returns related votes', function () {
    $voteCollection = VoteCollection::factory()->create();

    Vote::factory([
        'vote_collection_id' => $voteCollection,
    ])->count(3)->create();

    $vote = Vote::first();
    $relatedVotes = $vote->relatedVotes()->get();

    expect($relatedVotes->count())->toEqual(2);
    expect($relatedVotes->pluck('id'))->not()->toContain($vote->id);
});

it('returns primary vote', function () {
    $voteCollection = VoteCollection::factory()->create();

    $nonPrimary = Vote::factory([
        'vote_collection_id' => $voteCollection,
        'type' => VoteTypeEnum::AMENDMENT(),
    ])->create();

    $primary = Vote::factory([
        'vote_collection_id' => $voteCollection,
        'type' => VoteTypeEnum::PRIMARY(),
    ])->create();

    expect($nonPrimary->primaryVote->id)->toEqual($primary->id);
});

it('returns a subtitle for amendments', function () {
    $vote = Vote::factory([
        'type' => VoteTypeEnum::AMENDMENT(),
        'amendment' => 10,
        'author' => 'S&D',
    ])->make();

    expect($vote->subtitle)->toEqual('Amendment 10 by S&D');
});

it('returns a subtitle for separate votes', function () {
    $vote = Vote::factory([
        'type' => VoteTypeEnum::SEPARATE(),
        'subject' => '§ 10',
    ])->make();

    expect($vote->subtitle)->toEqual('Separate vote on § 10');
});

it('returns a subtitle for separate votes with split part', function () {
    $vote = Vote::factory([
        'type' => VoteTypeEnum::SEPARATE(),
        'subject' => '§ 10',
        'split_part' => '2',
    ])->make();

    expect($vote->subtitle)->toEqual('Separate vote on § 10/2');
});

it('returns a subtitle for primary votes', function () {
    $vote = Vote::factory([
        'type' => VoteTypeEnum::PRIMARY(),
    ])->make();

    expect($vote->subtitle)->toEqual('Final vote');
});
