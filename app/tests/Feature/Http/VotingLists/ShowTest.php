<?php

use App\Enums\CountryEnum;
use App\Enums\VoteResultEnum;
use App\Enums\VoteTypeEnum;
use App\Group;
use App\Member;
use App\Summary;
use App\Vote;
use App\VoteCollection;
use App\VotingList;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Support\Carbon;

uses(Tests\TestCase::class, RefreshDatabase::class);

beforeEach(function () {
    $date = new Carbon('2021-05-23');

    $this->greens = Group::factory([
        'code' => 'GREENS',
        'name' => 'Greens/European Free Alliance',
        'abbreviation' => 'Greens/EFA',
    ])->create();

    $this->sd = Group::factory([
        'code' => 'SD',
        'name' => 'Progressive Alliance of Socialists and Democrats',
        'abbreviation' => 'S&D',
    ])->create();

    $greensFor = Member::factory([
        'first_name' => 'Jane',
        'last_name' => 'DOE',
        'country' => CountryEnum::NL(),
    ])->activeAt($date, $this->greens)->count(1);

    $sdAgainst = Member::factory([
        'first_name' => 'Martin',
        'last_name' => 'EISENBAHN',
        'country' => CountryEnum::DE(),
    ])->activeAt($date, $this->sd)->count(2);

    $voteCollection = VoteCollection::factory(['title' => 'My Title'])->create();

    $votingListDataFinal = [
        'id' => 1,
        'description' => 'Matched Voting List',
        'date'=> $date,
        'vote_id' => Vote::factory([
            'type' => VoteTypeEnum::PRIMARY(),
            'result' => VoteResultEnum::ADOPTED(),
            'vote_collection_id' => $voteCollection,
            'final' => true,
        ]),
    ];

    $this->votingList = VotingList::factory($votingListDataFinal)
        ->withStats()
        ->withMembers('FOR', $greensFor)
        ->withMembers('AGAINST', $sdAgainst)
        ->create();

    $votingListDataNotFinal = [
        'id' => 2,
        'description' => 'Matched Voting List For Non Final Vote',
        'date'=> $date,
        'vote_id' => Vote::factory([
            'type' => VoteTypeEnum::SEPARATE(),
            'result' => VoteResultEnum::ADOPTED(),
            'vote_collection_id' => $voteCollection,
        ]),
    ];

    $this->votingListNonFinal = VotingList::factory($votingListDataNotFinal)
            ->withStats()
            ->withMembers('FOR', $greensFor)
            ->withMembers('AGAINST', $sdAgainst)
            ->create();
});

it('does not fail if there is no associated vote', function () {
    $votingList = VotingList::factory([
        'id' => 10,
        'vote_id' => null,
        'description' => 'Unmatched Voting List',
    ])->withStats()->create();

    $response = $this->get('/votes/10');
    expect($response)->toHaveStatus(200);
});

it('shows a title', function () {
    $response = $this->get('/votes/1');
    expect($response)->toHaveSelectorWithText('h1', 'My Title');
});

it('shows the result of the vote', function () {
    $response = $this->get('/votes/1');
    expect($response)->toHaveSelectorWithText('h1 + p', 'adopted');
    expect($response)->toHaveSelector('h1 + p > strong .thumb--adopted.thumb--circle');
});

it('displays a bar chart', function () {
    $response = $this->get('/votes/1');
    expect($response)->toHaveSelector('.vote-result-chart');
});

it('shows a list of members', function () {
    $response = $this->get('/votes/1');

    expect($response)->toHaveSelectorWithText('[role="tabpanel"] .list-item__text', 'Jane DOE');
    expect($response)->toHaveSelectorWithText('.list-item__text', 'Greens/EFA · Netherlands');
    expect($response)->toHaveSelector('.thumb--for.thumb--circle.list-item__thumb');
});

it('shows a list of groups sorted descending by number of active members', function () {
    $this->votingList->stats = array_merge($this->votingList->stats, [
        'by_group' => [
            $this->sd->id => [
                'active' => 100,
                'voted' => 25,
                'by_position' => [
                    'FOR' => 25,
                    'AGAINST' => 0,
                    'ABSTENTION' => 0,
                    'ABSENT' => 0,
                ],
            ],
            $this->greens->id => [
                'active' => 50,
                'voted' => 50,
                'by_position' => [
                    'FOR' => 50,
                    'AGAINST' => 0,
                    'ABSTENTION' => 0,
                    'ABSENT' => 0,
                ],
            ],
        ],
    ]);

    $this->votingList->save();
    $response = $this->get('/votes/1');
    expect($response)->toHaveSelectorWithText('[role="tabpanel"] .list-item__text', 'Progressive Alliance of Socialists and Democrats');
    expect($response)->toSeeInOrder([
        'Progressive Alliance of Socialists and Democrats',
        'Greens/European Free Alliance',
    ]);
});

it('shows all countries of which MEPs participated sorted descending by number of active members', function () {
    $this->votingList->stats = array_merge($this->votingList->stats, [
        'by_country' => [
            'DE' => [
                'active' => 100,
                'voted' => 25,
                'by_position' => [
                    'FOR' => 25,
                    'AGAINST' => 0,
                    'ABSTENTION' => 0,
                    'ABSENT' => 0,
                ],
            ],
            'NL' => [
                'active' => 200,
                'voted' => 50,
                'by_position' => [
                    'FOR' => 50,
                    'AGAINST' => 0,
                    'ABSTENTION' => 0,
                    'ABSENT' => 0,
                ],
            ],
        ],
    ]);

    $this->votingList->save();
    $response = $this->get('/votes/1');

    expect($response)->toHaveSelectorWithText('[role="tabpanel"] .list-item__text', 'Netherlands');
    expect($response)->toSeeInOrder([
        'Netherlands',
        'Germany',
    ]);
});

it('shows a panel for link to related votes if associated vote is final', function () {
    $response = $this->get('/votes/1');
    expect($response)->toHaveSelectorWithText('.action-panel', 'Related Votes');

    $response = $this->get('/votes/2');

    expect($response)->not()->toHaveSelectorWithText('.action-panel', 'Related Votes');
});

it('has share meta tags', function () {
    Storage::fake('public');
    Storage::disk('public')->put('share-pictures/vote-sharepic-1.png', 'test');

    $response = $this->get('/votes/1');
    expect($response)->toHaveSelector('meta[property="og:image"][content$="vote-sharepic-1.png"]');
    expect($response)->toHaveSelector('meta[property="og:image:alt"][content^="A barchart visualizing"]');
});

it('has default share meta tags if vote is not final', function () {
    Storage::fake('public');
    Storage::disk('public')->put('share-pictures/vote-sharepic-2.png', 'test');

    $response = $this->get('/votes/2');
    expect($response)->toHaveSelector('meta[property="og:image"][content$="default-share-picture.png"]');
    expect($response)->toHaveSelector('meta[property="og:image:alt"][content^="A photo of the hemicycle"]');
});

it('displays share button for final votes', function () {
    $response = $this->get('/votes/1');
    expect($response)->toHaveSelector('.share-button');

    $response = $this->get('/votes/2');
    expect($response)->not()->toHaveSelector('.share-button');
});

it('shows a callout if associated vote is not final', function () {
    $response = $this->get('/votes/2');

    expect($response)->toHaveSelector('.callout');

    $response = $this->get('/votes/1');

    expect($response)->not()->toHaveSelector('.callout--warning');
});

it('callout shows appropriate text for non-final votes', function () {
    $response = $this->get('/votes/2');
    expect($response)->toHaveSelectorWithText('.callout--warning', 'separate');

    $vote = VotingList::find(2)->vote;
    $vote->type = VoteTypeEnum::AMENDMENT();
    $vote->save();

    $response = $this->get('/votes/2');
    expect($response)->toHaveSelectorWithText('.callout--warning', 'amendment');
});

it('does not show a url in callout for a non-matched final vote', function () {
    $collection = VoteCollection::factory()->create();

    VotingList::factory([
        'id' => 10,
        'vote_id' => Vote::factory([
            'vote_collection_id' => $collection,
            'type' => VoteTypeEnum::SEPARATE(),
        ]),
    ])->withStats()->create();

    Vote::factory([
        'vote_collection_id' => $collection,
        'type' => VoteTypeEnum::PRIMARY(),
        'final' => true,
    ])->create();

    $response = $this->get('/votes/10');
    expect($response)->toHaveStatus(200);
    expect($response)->not()->toHaveSelectorWithText('.callout--warning', 'result of the final vote');
});

it('displays summary for final votes', function () {
    Summary::factory([
        'reference' => $this->votingList->vote->voteCollection->reference,
        'oeil_id' => 1234567,
        'text' => "First paragraph is stripped.\n\nThis is the summary.",
    ])->create();

    $response = $this->get('/votes/1');

    expect($response)->toHaveSelectorWithText('p', 'This is the summary.');
});

it('does not display summary for non-final votes', function () {
    Summary::factory([
        'reference' => $this->votingListNonFinal->vote->voteCollection->reference,
        'oeil_id' => 1234567,
        'text' => "First paragraph is stripped.\n\nThis is the summary.",
    ])->create();

    $response = $this->get('/votes/2');

    expect($response)->not()->toHaveSelectorWithText('p', 'This is the summary.');
});

it('is reachable with short url', function () {
    $hashId = VotingList::find(1)->hash_id;
    $response = $this->get("/{$hashId}");
    expect($response)->toRedirectTo(route('voting-list.show', ['votingList' => 1]));
});

it('returns 404 for non-existent short-url', function () {
    $response = $this->get('hash01');
    expect($response)->toHaveStatus(404);
});
