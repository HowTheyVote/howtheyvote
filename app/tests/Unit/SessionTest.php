<?php

use App\Enums\VoteTypeEnum;
use App\Session;
use App\Vote;
use Illuminate\Foundation\Testing\RefreshDatabase;

uses(Tests\TestCase::class, RefreshDatabase::class);
beforeEach(function () {
    $this->session = Session::factory([
        'start_date' => '2021-08-11',
        'end_date' => '2021-08-15',
    ])->create();
});

it('has a display title', function () {
    expect($this->session->display_title)->toEqual('Session from 2021-08-11 to 2021-08-15');
});

it('returns primary votes', function () {
    Vote::factory([
        'type' => VoteTypeEnum::PRIMARY(),
        'session_id' => $this->session,
    ])->create();

    Vote::factory([
        'type' => VoteTypeEnum::SEPARATE(),
        'session_id' => $this->session,
    ])->create();

    expect($this->session->primaryVotes()->count())->toEqual(1);
    expect($this->session->primaryVotes()->first())->toEqual(Vote::find(1));
});
