<?php

use App\Enums\LocationEnum;
use App\Enums\VoteTypeEnum;
use App\Session;
use App\Vote;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Support\Carbon;

uses(Tests\TestCase::class, RefreshDatabase::class);

it('has a display title', function () {
    $session = Session::factory([
        'start_date' => '2021-08-11',
        'end_date' => '2021-08-15',
        'location' => LocationEnum::BRUSSELS,
    ])->create();

    expect($session->display_title)->toEqual('August 2021 · Brussels');
});

it('returns final votes', function () {
    $session = Session::factory()->create();

    $finalVote = Vote::factory([
        'type' => VoteTypeEnum::SEPARATE,
        'final' => true,
        'session_id' => $session,
    ])->create();

    Vote::factory([
        'type' => VoteTypeEnum::PRIMARY,
        'session_id' => $session,
    ])->create();

    expect($session->votes()->final()->count())->toEqual(1);
    expect($session->votes()->final()->first()->id)->toEqual($finalVote->id);
});

it('returns next session', function () {
    $next = Session::factory([
        'start_date' => '2021-09-01',
        'end_date' => '2021-09-05',
    ])->create();

    Session::factory([
        'start_date' => '2021-10-01',
        'end_date' => '2021-10-05',
    ])->create();

    Carbon::setTestNow('2021-08-01');
    expect(Session::next()->id)->toEqual($next->id);
});

it('returns last session', function () {
    Session::factory([
        'start_date' => '2021-08-01',
        'end_date' => '2021-08-05',
    ])->create();

    $last = Session::factory([
        'start_date' => '2021-09-01',
        'end_date' => '2021-09-05',
    ])->create();

    Carbon::setTestNow('2021-10-01');
    expect(Session::last()->id)->toEqual($last->id);
});

it('returns current session', function () {
    $session = Session::factory([
        'start_date' => '2021-09-01',
        'end_date' => '2021-09-05',
    ])->create();

    Carbon::setTestNow('2021-09-02');
    expect(Session::current()->id)->toEqual($session->id);
});

it('returns null if there is no current session', function () {
    $session = Session::factory([
        'start_date' => '2021-09-01',
        'end_date' => '2021-09-05',
    ])->create();

    Carbon::setTestNow('2021-10-01');
    expect(Session::current())->toBeNull();
});

it('has a link to its agenda', function () {
    $session = Session::factory([
        'start_date' => '2021-09-01',
        'end_date' => '2021-09-05',
    ])->create();

    expect($session->agenda_url)->toEqual('https://www.europarl.europa.eu/doceo/document/OJ-9-2021-09-01-SYN_EN.html');
});
