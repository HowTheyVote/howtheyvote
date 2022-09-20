<?php

use App\Enums\LocationEnum;
use App\Session;
use App\Vote;
use App\VotingList;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Support\Carbon;

uses(Tests\TestCase::class, RefreshDatabase::class);

beforeEach(function () {
    $this->currentSession = Session::factory([
        'start_date' => '2021-08-01',
        'end_date' => '2021-08-04',
        'location' => LocationEnum::STRASBOURG(),
    ])->create();

    $this->lastSession = Session::factory([
        'start_date' => '2021-07-01',
        'end_date' => '2021-07-04',
        'location' => LocationEnum::STRASBOURG(),

    ])->create();

    $this->nextSession = Session::factory([
        'start_date' => '2021-09-01',
        'end_date' => '2021-09-04',
        'location' => LocationEnum::BRUSSELS(),
    ])->create();

    Carbon::setTestNow('2021-08-02');
});

it('displays date of current session', function () {
    $view = $this->blade('<x-session-display :currentSession="$currentSession" :lastSession="$lastSession" :nextSession="$nextSession" />', [
        'currentSession' => $this->currentSession,
        'lastSession' => $this->lastSession,
        'nextSession' => $this->nextSession,
    ]);

    expect($view)->toSeeText('Parliament is meeting in Strasbourg this week.');
});

it('displays link to the agenda of the session', function () {
    $view = $this->blade('<x-session-display :currentSession="$currentSession" :lastSession="$lastSession" :nextSession="$nextSession" />', [
        'currentSession' => $this->currentSession,
        'lastSession' => $this->lastSession,
        'nextSession' => $this->nextSession,
    ]);

    expect($view)->toHaveSelectorWithText('a[href="https://www.europarl.europa.eu/doceo/document/OJ-9-2021-08-01-SYN_EN.html"]', 'agenda');
});

it('displays date of next session', function () {
    $vote = Vote::factory([
        'session_id' => $this->lastSession->id,
        'final' => true,
    ])->create();

    VotingList::factory([
        'vote_id' => $vote->id,
    ])->create();

    $view = $this->blade('<x-session-display :currentSession="$currentSession" :lastSession="$lastSession" :nextSession="$nextSession" />', [
        'currentSession' => null,
        'lastSession' => $this->lastSession,
        'nextSession' => $this->nextSession,
    ]);

    expect($view)->toSeeText('The next plenary session will be held in Brussels from Sep 1st to Sep 4th.');
});

it('displays date of last session if vote results are not yet avaiable', function () {
    $view = $this->blade('<x-session-display :currentSession="$currentSession" :lastSession="$lastSession" :nextSession="$nextSession" />', [
        'currentSession' => null,
        'lastSession' => $this->lastSession,
        'nextSession' => $this->nextSession,
    ]);

    expect($view)->toSeeText('The last plenary session was held from Jul 1st to Jul 4th in Strasbourg.');
});
