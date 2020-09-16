<?php

use App\GroupMembership;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Support\Carbon;

uses(Tests\TestCase::class, RefreshDatabase::class);

it('filters active memberships for given date', function () {
    $date = new Carbon('2020-01-02');
    $before = new Carbon('2020-01-01');
    $after = new Carbon('2020-01-03');

    GroupMembership::factory()->activeAt($before)->create();
    GroupMembership::factory()->activeAt($after)->create();
    $active = GroupMembership::factory()->activeAt($date)->create();

    expect(GroupMembership::activeAt($date)->count())->toEqual(1);
    expect(GroupMembership::activeAt($date)->first()->is($active))->toBeTrue();
});
