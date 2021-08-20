<?php

use App\Enums\LocationEnum;
use App\Enums\VoteTypeEnum;
use App\Session;
use App\Vote;
use Illuminate\Foundation\Testing\RefreshDatabase;

uses(Tests\TestCase::class, RefreshDatabase::class);
beforeEach(function () {
    $this->session = Session::factory([
        'start_date' => '2021-08-11',
        'end_date' => '2021-08-15',
        'location' => LocationEnum::BRUSSELS(),
    ])->create();
});

it('has a display title', function () {
    expect($this->session->display_title)->toEqual('August 2021 · Brussels');
});

it('returns final votes', function () {
    $finalVote = Vote::factory([
        'type' => VoteTypeEnum::SEPARATE(),
        'final' => true,
        'session_id' => $this->session,
    ])->create();

    Vote::factory([
        'type' => VoteTypeEnum::PRIMARY(),
        'session_id' => $this->session,
    ])->create();

    expect($this->session->votes()->final()->count())->toEqual(1);
    expect($this->session->votes()->final()->first()->id)->toEqual($finalVote->id);
});
