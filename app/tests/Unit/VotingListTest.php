<?php

use App\Enums\VoteResultEnum;
use App\Enums\VoteTypeEnum;
use App\Vote;
use App\VoteCollection;
use App\VotingList;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Support\Carbon;
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
            'final' => true,
        ]),
    ])->make();

    expect($votingList->share_picture_url)->toBeNull();
});

it('returns link to sharepic if vote is final and picture does exist', function () {
    Storage::fake('public');
    Storage::disk('public')->put('share-pictures/vote-sharepic-1.png', 'test');

    $votingList = VotingList::factory([
        'date' => '2021-01-01',
        'id' => 1,
        'vote_id' => Vote::factory([
            'type' => VoteTypeEnum::AMENDMENT(),
            'final' => true,
        ]),
    ])->make();

    expect($votingList->share_picture_url)->toContain('share-pictures/vote-sharepic-1.png');
});

it('returns description of share pic', function () {
    $vote = Vote::factory(['final' => true]);

    $votingList = VotingList::factory(['vote_id' => $vote])
        ->withStats()
        ->withDate(Carbon::create('1993-02-02'))
        ->create();

    $expected = 'A barchart visualizing the result of the European Parliaments vote on "Children’s rights". The vote was held on Feb 2, 1993. The barchart has three bars, representing the 10 MEPs who voted in favor (17%), the 20 MEPs who votes against (33%), and the 30 MEPs who did abstain (50%). In total, 60 MEPs participated in the vote and 40 MEPs did not vote.';

    expect($votingList->share_picture_description)->toBe($expected);
});

it('returns result of matched vote', function () {
    $votingList = VotingList::factory()->make();

    expect($votingList->result_string)->toEqual('');
    expect($votingList->result)->toBeNull();

    $votingList = VotingList::factory([
        'vote_id' => Vote::factory([
            'result' => VoteResultEnum::ADOPTED(),
        ]),
    ])->make();

    expect($votingList->result_string)->toEqual(Str::lower(VoteResultEnum::ADOPTED()->label));
    expect($votingList->result)->toEqual(VoteResultEnum::ADOPTED());
});
