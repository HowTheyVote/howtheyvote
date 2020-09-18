<?php

use App\GroupMembership;
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
