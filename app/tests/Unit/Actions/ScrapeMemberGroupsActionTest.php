<?php

use App\Actions\ScrapeMemberGroupsAction;
use App\Group;
use App\GroupMembership;
use App\Member;
use App\Term;
use Illuminate\Foundation\Testing\RefreshDatabase;

uses(Tests\TestCase::class, RefreshDatabase::class);

beforeEach(function () {
    $this->action = $this->app->make(ScrapeMemberGroupsAction::class);

    $this->member = Member::factory(['web_id' => 12345])->create();
    $this->group = Group::factory(['code' => 'GREENS'])->create();
    $this->term = Term::factory(['number' => 8])->create();
});

it('creates new group membership records', function () {
    Http::fakeJsonFromFile('*/member_groups?web_id=12345&term=8', 'member_groups.json');

    $this->action->execute($this->member, $this->term);

    $memberships = $this->member->groupMemberships();

    expect($memberships->count())->toEqual(1);
    expect($memberships->first()->group->id)->toEqual($this->group->id);
    expect($memberships->first()->term->id)->toEqual($this->term->id);
    expect($memberships->first()->start_date)->toEqual('2014-07-02');
    expect($memberships->first()->end_date)->toBeNull();
});

it('updates existing group membership records', function () {
    Http::fakeJsonFromFile('*/member_groups?web_id=12345&term=8', 'member_groups-2.json');

    GroupMembership::factory([
        'member_id' => $this->member->id,
        'group_id' => $this->group->id,
        'term_id' => $this->term->id,
        'start_date' => '2014-07-02',
        'end_date' => null,
    ])->create();

    $this->action->execute($this->member, $this->term);

    $memberships = $this->member->groupMemberships();

    expect($memberships->count())->toEqual(1);
    expect($memberships->first()->start_date)->toEqual('2014-07-02');
    expect($memberships->first()->end_date)->toEqual('2019-07-01');
});
