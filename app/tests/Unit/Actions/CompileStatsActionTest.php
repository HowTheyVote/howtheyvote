<?php

use App\Actions\CompileStatsAction;
use App\Group;
use App\Member;
use App\VotingList;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Support\Carbon;

uses(Tests\TestCase::class, RefreshDatabase::class);

beforeEach(function () {
    $this->action = $this->app->make(CompileStatsAction::class);
    $this->date = new Carbon('2020-01-01');
});

it('compiles general stats', function () {
    $for = Member::factory()
        ->activeAt($this->date)
        ->count(3);

    $against = Member::factory()
        ->activeAt($this->date)
        ->count(2);

    $abstention = Member::factory()
        ->activeAt($this->date)
        ->count(1);

    $noVote = Member::factory()
        ->activeAt($this->date)
        ->count(1);

    $votingList = VotingList::factory()
        ->withDate($this->date)
        ->withMembers('FOR', $for)
        ->withMembers('AGAINST', $against)
        ->withMembers('ABSTENTION', $abstention)
        ->withMembers('NOVOTE', $noVote)
        ->create();

    $this->action->execute($votingList);

    $stats = $votingList->fresh()->stats;

    expect($stats['voted'])->toEqual(6);
    expect($stats['active'])->toEqual(7);
    expect($stats['by_position'])->toEqual([
        'FOR' => 3,
        'AGAINST' => 2,
        'ABSTENTION' => 1,
        'NOVOTE' => 1,
    ]);
});

it('compiles stats per country', function () {
    $deFor = Member::factory()
        ->country('DE')
        ->activeAt($this->date)
        ->count(1);

    $deAgainst = Member::factory()
        ->country('DE')
        ->activeAt($this->date)
        ->count(1);

    $frFor = Member::factory()
        ->country('FR')
        ->activeAt($this->date)
        ->count(2);

    $frNoVote = Member::factory()
        ->country('FR')
        ->activeAt($this->date)
        ->count(1);

    $votingList = VotingList::factory()
        ->withDate($this->date)
        ->withMembers('FOR', $deFor)
        ->withMembers('AGAINST', $deAgainst)
        ->withMembers('FOR', $frFor)
        ->withMembers('NOVOTE', $frNoVote)
        ->create();

    $this->action->execute($votingList);

    $stats = $votingList->fresh()->stats['by_country'];

    expect($stats['DE'])->toEqual([
        'voted' => 2,
        'active' => 2,
        'by_position' => [
            'FOR' => 1,
            'AGAINST' => 1,
            'ABSTENTION' => 0,
            'NOVOTE' => 0,
        ],
    ]);

    expect($stats['FR'])->toEqual([
        'voted' => 2,
        'active' => 3,
        'by_position' => [
            'FOR' => 2,
            'AGAINST' => 0,
            'ABSTENTION' => 0,
            'NOVOTE' => 1,
        ],
    ]);
});

it('compiles stats per group', function () {
    $greens = Group::factory(['code' => 'GREENS'])->create();
    $epp = Group::factory(['code' => 'EPP'])->create();

    $greensFor = Member::factory()
        ->activeAt($this->date, $greens)
        ->count(1);

    $eppAgainst = Member::factory()
        ->activeAt($this->date, $epp)
        ->count(2);

    $eppNoVote = Member::factory()
        ->activeAt($this->date, $epp)
        ->count(1);

    $votingList = VotingList::factory()
        ->withDate($this->date)
        ->withMembers('FOR', $greensFor)
        ->withMembers('AGAINST', $eppAgainst)
        ->withMembers('NOVOTE', $eppNoVote)
        ->create();

    $this->action->execute($votingList);

    $stats = $votingList->fresh()->stats['by_group'];

    expect($stats[$greens->id])->toEqual([
        'voted' => 1,
        'active' => 1,
        'by_position' => [
            'FOR' => 1,
            'AGAINST' => 0,
            'ABSTENTION' => 0,
            'NOVOTE' => 0,
        ],
    ]);

    expect($stats[$epp->id])->toEqual([
        'voted' => 2,
        'active' => 3,
        'by_position' => [
            'FOR' => 0,
            'AGAINST' => 2,
            'ABSTENTION' => 0,
            'NOVOTE' => 1,
        ],
    ]);
});
