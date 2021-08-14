<?php

use App\Enums\VoteTypeEnum;
use App\Vote;
use App\VoteCollection;
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
        'vote_id' => Vote::factory([
            'vote_collection_id' => VoteCollection::factory([
                'title' => 'Blub',
            ]),
        ]),
    ])->make();

    expect($votingList->display_title)->toEqual('Blub');
});

it('has a formatted date', function () {
    $votingList = VotingList::factory([
        'date' => '2021-01-01',
    ])->make();

    expect($votingList->formatted_date)->toEqual('Friday, January 1, 2021');
});

it('does not return a sharepic link if it has no vote', function () {
    $votingList = VotingList::factory([
        'date' => '2021-01-01',
    ])->make();

    expect($votingList->share_picture_url)->toBeNull();
});

it('does not return a sharepic link if it the picture does not exist', function () {
    Storage::fake('public');

    $votingList = VotingList::factory([
        'date' => '2021-01-01',
        'id' => 1,
        'vote_id' => Vote::factory([
            'type' => VoteTypeEnum::PRIMARY(),
        ]),
    ])->make();

    expect($votingList->share_picture_url)->toBeNull();
});

it('returns link to sharepic if vote is primary and picture does exist', function () {
    Storage::fake('public');
    Storage::disk('public')->put('share-pictures/vote-sharepic-1.png', 'test');

    $votingList = VotingList::factory([
        'date' => '2021-01-01',
        'id' => 1,
        'vote_id' => Vote::factory([
            'type' => VoteTypeEnum::PRIMARY(),
        ]),
    ])->make();

    expect($votingList->share_picture_url)->toContain('share-pictures/vote-sharepic-1.png');
});
