<?php

use App\Enums\VoteTypeEnum;
use App\Session;
use App\Vote;
use App\VotingList;
use Illuminate\Foundation\Testing\RefreshDatabase;

uses(Tests\TestCase::class, RefreshDatabase::class);

beforeEach(function () {
    VotingList::factory([
        'vote_id' => Vote::factory([
            'session_id' => Session::factory()->create(),
            'type' => VoteTypeEnum::PRIMARY(),
        ]),
    ])->count(2)
    ->create();
});

it('renders successfully', function () {
    $response = $this->get('/votes');
    expect($response)->toHaveStatus(200);
});

it('shows a vote card for each existing vote', function () {
    $response = $this->get('/votes');
    expect($response)->toHaveSelector('.vote-card', 2);
});

it('renders the session titles', function () {
    $response = $this->get('/votes');
    expect($response)->toHaveSelectorWithText('.beta', 'Session from');
});
