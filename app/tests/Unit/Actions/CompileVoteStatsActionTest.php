<?php

use App\Actions\CompileVoteStatsAction;
use App\Vote;
use Illuminate\Foundation\Testing\RefreshDatabase;

uses(Tests\TestCase::class, RefreshDatabase::class);

it('compiles general stats', function () {
    $vote = Vote::factory()
        ->withFor(3)
        ->withAgainst(2)
        ->withAbstention(1)
        ->create();

    $this->action = $this->app->make(CompileVoteStatsAction::class);

    $this->action->execute($vote);

    $vote = $vote->fresh();

    expect($vote->stats['voted'])->toEqual(6);
    expect($vote->stats['active'])->toEqual(6);

    expect($vote->stats['by_position']['FOR'])->toEqual(3);
    expect($vote->stats['by_position']['AGAINST'])->toEqual(2);
    expect($vote->stats['by_position']['ABSTENTION'])->toEqual(1);
});
