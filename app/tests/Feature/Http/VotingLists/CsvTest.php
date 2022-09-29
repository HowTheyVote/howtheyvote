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
        'id' => 1,
    ])->activeAt($date, $greens)->count(1);

    // MEP that got created second, comes earlier in the alphabet!
    $this->greensAgainst = Member::factory([
        'first_name' => 'Jane',
        'last_name' => 'BOE',
        'country' => CountryEnum::NL(),
        'id' => 2,
    ])->activeAt($date, $greens)->count(1);

    $this->votingList = VotingList::factory(['date' => $date])
        ->withMembers('FOR', $this->greensFor)
        ->withMembers('AGAINST', $this->greensAgainst)
        ->create();
});

it('creates a csv with one row per member, sorted alphabetically', function () {
    $response = $this->get("/votes/{$this->votingList->id}.csv");
    $expected = "member_id,last_name,first_name,group.abbreviation,group.name,country.code,country.name,position\n";
    $expected .= "2,BOE,Jane,Greens/EFA,\"Greens/European Free Alliance\",NL,Netherlands,AGAINST\n";
    $expected .= "1,DOE,Jane,Greens/EFA,\"Greens/European Free Alliance\",NL,Netherlands,FOR\n";

    expect(Member::count())->toEqual(2);

    expect($response->content())->toEqual($expected);
});

it('sets correct content type', function () {
    $response = $this->get("/votes/{$this->votingList->id}.csv");
    expect($response)->toHaveHeader('Content-Type', 'text/csv; charset=UTF-8');
});
