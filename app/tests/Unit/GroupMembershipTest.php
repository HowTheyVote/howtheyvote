<?php

use App\GroupMembership;
use App\Term;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Support\Carbon;

uses(Tests\TestCase::class, RefreshDatabase::class);

it('filters active memberships for given date', function () {
    $date = new Carbon('2020-01-02');
    $before = new Carbon('2020-01-01');
    $after = new Carbon('2020-01-03');

    GroupMembership::factory()
        ->withDate($before)
        ->create();

    GroupMembership::factory()
        ->withDate($after)
        ->create();

    $active = GroupMembership::factory()
        ->withDate($date)
        ->create();

    $memberships = GroupMembership::activeAt($date);

    expect($memberships->count())->toEqual(1);
    expect($memberships->first()->is($active))->toBeTrue();
});

it('filters ongoing active memberships for given date', function () {
    $date = new Carbon('2020-01-01');

    GroupMembership::factory([
        'start_date' => $date,
        'end_date' => null,
    ])->create();

    expect(GroupMembership::activeAt($date)->count())->toEqual(1);
});

it('filters active memberships for given date and term', function () {
    $date = new Carbon('2020-01-01');

    $firstTerm = Term::factory(['number' => 8])->create();
    $secondTerm = Term::factory(['number' => 9])->create();

    $active = GroupMembership::factory([
        'term_id' => $firstTerm,
        'start_date' => $date,
        'end_date' => null,
    ])->create();

    GroupMembership::factory([
        'term_id' => $secondTerm,
        'start_date' => $date,
        'end_date' => null,
    ])->create();

    $memberships = GroupMembership::activeAt($date, $firstTerm);

    expect($memberships->count())->toEqual(1);
    expect($memberships->first()->is($active))->toBeTrue();
});
