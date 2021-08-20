<?php

use App\Enums\LocationEnum;
use App\Enums\VoteTypeEnum;
use App\Session;
use App\Vote;
use App\VotingList;
use Illuminate\Foundation\Testing\RefreshDatabase;

uses(Tests\TestCase::class, RefreshDatabase::class);

beforeEach(function () {
    VotingList::factory([
        'vote_id' => Vote::factory([
            'session_id' => Session::factory([
                'start_date' => '2021-01-01',
                'end_date' => '2021-01-05',
                'location' => LocationEnum::BRUSSELS(),
            ])->create(),
            'final' => true,
        ]),
    ])->count(2)
    ->create();
});

it('renders successfully', function () {
    $response = $this->get('/votes');
    expect($response)->toHaveStatus(200);
});

it('shows a vote card for each existing final vote', function () {
    $response = $this->get('/votes');
    expect($response)->toHaveSelector('.vote-card', 2);
});

it('renders the session titles', function () {
    $response = $this->get('/votes');
    expect($response)->toHaveSelectorWithText('.beta', 'January 2021 · Brussels');
});

it('does not include final votes that have not been matched to a voting list', function () {
    Vote::factory([
            'session_id' => Session::first(),
            'type' => VoteTypeEnum::PRIMARY(),
            'final' => true,
    ])->create();

    Vote::factory([
        'session_id' => Session::first(),
        'type' => VoteTypeEnum::SEPARATE(),
        'final' => true,
    ])->create();

    $response = $this->get('/votes');
    expect($response)->toHaveSelector('.vote-card', 2);
});

it('does not show session-headings for sessions without matched final votes', function () {
    // matched but not final
    VotingList::factory([
        'vote_id' => Vote::factory([
            'session_id' => Session::factory([
                'start_date' => '2021-01-05',
                'end_date' => '2021-01-08',
                'location' => LocationEnum::BRUSSELS(),
            ])->create(),
        ]),
    ])->create();

    // final but not matched
    Vote::factory([
            'session_id' => Session::factory([
                'start_date' => '2021-03-05',
                'end_date' => '2021-03-08',
                'location' => LocationEnum::BRUSSELS(),
            ]),
    ])->create();

    $response = $this->get('/votes');
    expect($response)->toHaveSelector('.vote-card', 2);
});
