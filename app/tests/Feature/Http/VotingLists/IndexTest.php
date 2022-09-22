<?php

use App\Enums\LocationEnum;
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
                'location' => LocationEnum::BRUSSELS,
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
