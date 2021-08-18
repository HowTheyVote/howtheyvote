<?php

use App\Enums\CountryEnum;
use App\Group;
use App\Member;
use App\VotingList;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Support\Carbon;

uses(Tests\TestCase::class, RefreshDatabase::class);

beforeEach(function () {
    $date = new Carbon('2021-05-23');

    $greens = Group::factory([
        'code' => 'GREENS',
        'name' => 'Greens/European Free Alliance',
        'abbreviation' => 'Greens/EFA',
    ])->create();

    $this->greensFor = Member::factory([
        'first_name' => 'Jane',
        'last_name' => 'DOE',
        'country' => CountryEnum::NL(),
    ])->activeAt($date, $greens)->count(1);

    $this->votingList = VotingList::factory(['date' => $date])
        ->withMembers('FOR', $this->greensFor)
        ->create();
});

it('creates a csv with one row per member', function () {
    $response = $this->get("/votes/{$this->votingList->id}.csv");
    $expectedId = $this->votingList->members->last()->id;
    $expected = "member_id,last_name,first_name,group.abbreviation,group.name,country.code,country.name,position\n";
    $expected .= "{$expectedId},DOE,Jane,Greens/EFA,\"Greens/European Free Alliance\",NL,Netherlands,FOR\n";

    expect(Member::count())->toEqual(1);

    expect($response->content())->toEqual($expected);
});

it('sets correct content type', function () {
    $response = $this->get("/votes/{$this->votingList->id}.csv");
    expect($response)->toHaveHeader('Content-Type', 'text/csv; charset=UTF-8');
});
