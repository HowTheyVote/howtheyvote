<?php

use App\Actions\ScrapeAndSaveMemberGroupsAction;
use App\Group;
use App\Member;
use App\Term;
use Illuminate\Foundation\Testing\RefreshDatabase;

uses(Tests\TestCase::class, RefreshDatabase::class);

beforeEach(function () {
    $this->action = $this->app->make(ScrapeAndSaveMemberGroupsAction::class);

    $this->member = Member::factory(['web_id' => 12345])->create();
    $this->group = Group::factory(['code' => 'GREENS'])->create();
    $this->term = Term::factory(['number' => 8])->create();
});

it('creates new group membership records', function () {
    Http::fakeJsonFromFile('*/member_groups?web_id=12345&term=8', 'member_groups.json');

    $this->action->execute(12345, 8);

    $memberships = $this->member->groupMemberships();

    expect($memberships->count())->toEqual(1);
    expect($memberships->first()->group->id)->toEqual($this->group->id);
    expect($memberships->first()->term->id)->toEqual($this->term->id);

    expect($memberships->first()->start_date)->toEqual('2014-07-02');
    expect($memberships->first()->end_date)->toBeNull();
});

it('updates existing group membership records', function () {
    Http::fakeJsonSequenceFromFile(
        '*/member_groups?web_id=12345&term=8',
        ['member_groups.json', 'member_groups-2.json']
    );

    $this->action->execute(12345, 8);

    $memberships = $this->member->groupMemberships();

    expect($memberships->count())->toEqual(1);
    expect($memberships->first()->end_date)->toBeNull();

    $this->action->execute(12345, 8);

    expect($memberships->count())->toEqual(1);
    expect($memberships->first()->start_date)->toEqual('2014-07-02');
    expect($memberships->first()->end_date)->toEqual('2019-07-01');
});
