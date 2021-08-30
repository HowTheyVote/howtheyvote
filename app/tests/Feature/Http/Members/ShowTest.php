<?php

use App\Enums\CountryEnum;
use App\Enums\VoteResultEnum;
use App\Group;
use App\Member;
use App\Vote;
use App\VotingList;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Support\Carbon;

uses(Tests\TestCase::class, RefreshDatabase::class);

beforeEach(function () {
    $this->firstJan = new Carbon('2020-01-01');
    $this->thirdJan = new Carbon('2020-01-03');
    Carbon::setTestNow($this->thirdJan);

    $greens = Group::factory([
        'code' => 'GREENS',
        'name' => 'Greens/European Free Alliance',
        'abbreviation' => 'Greens/EFA',
    ])->create();

    $this->member = Member::factory([
        'first_name' => 'Jane',
        'last_name' => 'DOE',
        'country' => CountryEnum::NL(),
        'twitter' => '@handle',
    ])->activeAt($this->firstJan, $greens)
        ->activeAt($this->thirdJan, $greens)
        ->create();

    VotingList::factory(
        [
            'date' => $this->firstJan,
            'vote_id' => Vote::factory([
                'final' => true,
                'result' => VoteResultEnum::REJECTED(),
            ]),
        ])
        ->create()
        ->members()
        ->attach($this->member->id, ['position' => 'AGAINST']);

    VotingList::factory(
        [
            'date' => $this->thirdJan,
            'vote_id' => Vote::factory([
                'final' => true,
                'result' => VoteResultEnum::REJECTED(),
            ]),
        ])
        ->create()
        ->members()
        ->attach($this->member->id, ['position' => 'FOR']);

    VotingList::factory(
        [
            'date' => $this->firstJan,
            'vote_id' => Vote::factory([
                'final' => false,
                'result' => VoteResultEnum::ADOPTED(),
            ]),
        ])
        ->create()
        ->members()
        ->attach($this->member->id, ['position' => 'FOR']);

    $this->memberId = Member::first()->id;
});

afterEach(function () {
    Carbon::setTestNow();
});

it('renders successfully', function () {
    $response = $this->get("/members/{$this->memberId}");
    expect($response)->toHaveStatus(200);
});

it('lists final votes with position of member', function () {
    $response = $this->get("/members/{$this->memberId}");
    expect($response)->toHaveSelector('.thumb--for.thumb--circle', 1);
});

it('shows an info box with contact links for active members', function () {
    $response = $this->get("/members/{$this->memberId}");
    expect($response)->toHaveSelector("img[src$='/members/{$this->memberId}.jpg']");
    expect($response)->toHaveSelectorWithText('.member-header', 'Greens/European Free Alliance');
    expect($response)->toHaveSelectorWithText('.member-header', 'Netherlands');

    expect($response)->toHaveSelectorWithText('.member-header', 'Twitter');
    expect($response)->not()->toHaveSelectorWithText('member-header', 'Facebook');
});

it('shows contact info for non-active members', function () {
    Carbon::setTestNow();
    $response = $this->get("/members/{$this->memberId}");

    expect($response)->toHaveSelector("img[src$='/members/{$this->memberId}.jpg']");
    expect($response)->toHaveSelectorWithText('.member-header', 'Netherlands');
    expect($response)->toHaveSelectorWithText('.member-header', 'Twitter');
    expect($response)->not()->toHaveSelectorWithText('.member-header', 'Facebook');
});

it('shows votes in reverse chronological order', function () {
    $response = $this->get("/members/{$this->memberId}");
    expect($response)->toSeeInOrder([
        'Friday, January 3, 2020',
        'Wednesday, January 1, 2020',
    ]);
});
