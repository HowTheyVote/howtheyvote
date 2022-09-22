<?php

use App\Enums\CountryEnum;
use App\Enums\VoteResultEnum;
use App\Group;
use App\Member;
use App\Vote;
use App\VoteCollection;
use App\VotingList;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Support\Carbon;

uses(Tests\TestCase::class, RefreshDatabase::class);

beforeEach(function () {
    $date = new Carbon('2021-05-23');
    $display_title = 'Budged 2020';

    $greens = Group::factory([
        'code' => 'GREENS',
        'name' => 'Greens/European Free Alliance',
        'abbreviation' => 'Greens/EFA',
    ])->create();

    $this->greensFor = Member::factory([
        'first_name' => 'Jane',
        'last_name' => 'DOE',
        'country' => CountryEnum::NL,
    ])->activeAt($date, $greens)->count(1);

    $this->votingList = VotingList::factory([
        'date' => $date,
        'vote_id' => Vote::factory([
            'result' => VoteResultEnum::REJECTED,
            'vote_collection_id' => VoteCollection::factory([
                'title' => 'Budget 2020',
            ]),
        ]),
        'description' => 'Budged 2020',
    ])
        ->withMembers('FOR', $this->greensFor)
        ->create();
});

it('creates a JSON with one row per member', function () {
    $response = $this->get("/votes/{$this->votingList->id}.json")->json();

    $expected = [
        'title' => 'Budget 2020',
        'date' => '2021-05-23T00:00:00.000000Z',
        'result' => 'rejected',
        'members' => [
            [
                'member_id' => $this->votingList->members()->first()->id,
                'last_name' => 'DOE',
                'first_name' => 'Jane',
                'group' => [
                    'abbreviation' => 'Greens/EFA',
                    'name' => 'Greens/European Free Alliance',
                ],
                'country' => [
                    'code' => 'NL',
                    'name' => 'Netherlands',
                ],
                'position' => 'FOR',
            ],
        ],
    ];

    expect(Member::count())->toEqual(1);
    expect($response)->toEqual($expected);
});

it('sets correct content type', function () {
    $response = $this->get("/votes/{$this->votingList->id}.json");
    expect($response)->toHaveHeader('Content-Type', 'application/json');
});
