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
    $this->date = new Carbon('2020-01-01');

    $greens = Group::factory([
        'code' => 'GREENS',
        'name' => 'Greens/European Free Alliance',
        'abbreviation' => 'Greens/EFA',
    ])->create();

    $this->greensFor = Member::factory([
        'first_name' => 'Jane',
        'last_name' => 'DOE',
        'country' => CountryEnum::NL(),
        'twitter' => '@handle',
    ])->activeAt($this->date, $greens)->count(1);

    $this->votingList = VotingList::factory(
        [
            'date' => $this->date,
            'vote_id' => Vote::factory([
                'final' => true,
                'result' => VoteResultEnum::REJECTED(),
            ]),
        ])
        ->withMembers('FOR', $this->greensFor)
        ->create();

    $this->votingList = VotingList::factory(
            [
                'date' => $this->date,
                'vote_id' => Vote::factory([
                    'final' => false,
                    'result' => VoteResultEnum::ADOPTED(),
                ]),
            ])
            ->withMembers('FOR', $this->greensFor)
            ->create();

    $this->memberId = Member::first()->id;
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
    Carbon::setTestNow($this->date);

    $response = $this->get("/members/{$this->memberId}");
    expect($response)->toHaveSelector('.member-card', 1);
    expect($response)->toSeeText('Netherlands');
    expect($response)->toSeeText('Twitter');
    expect($response)->not()->toSeeText('Facebook');
    expect($response)->toSee("/members/{$this->memberId}");

    expect($response)->toSeeText('Greens/European Free Alliance');

    Carbon::setTestNow();
});

it('shows contact info for non-active members', function () {
    $response = $this->get("/members/{$this->memberId}");
    expect($response)->toHaveSelector('.member-card', 1);
    expect($response)->toSeeText('Netherlands');
    expect($response)->toSeeText('Twitter');
    expect($response)->not()->toSeeText('Facebook');
    expect($response)->toSee("/members/{$this->memberId}");

    expect($response)->toSeeText('not affiliated');
});
