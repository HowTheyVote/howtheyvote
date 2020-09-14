<?php

use App\Member;
use App\Term;
use Illuminate\Database\QueryException;
use Illuminate\Foundation\Testing\RefreshDatabase;

uses(Tests\TestCase::class, RefreshDatabase::class);

it('ensures `web_id` is unique', function () {
    Member::factory()->createMany([
        ['web_id' => 12345],
        ['web_id' => 12345],
    ]);
})->throws(QueryException::class);

it('converts date_of_birth to date object', function () {
    $member = new Member([
        'date_of_birth' => '1975-01-01',
    ]);

    expect($member->date_of_birth)->toBeInstanceOf(DateTime::class);
});

it('merges terms', function () {
    Term::factory()->createMany([
        ['number' => 8],
        ['number' => 9],
        ['number' => 10],
    ]);

    $oldTerms = Term::whereIn('number', [8, 9]);
    $newTerms = Term::whereIn('number', [9, 10]);

    $member = Member::factory(['web_id' => 12345])->create();
    $member->terms()->attach($oldTerms->pluck('id'));

    $result = $member->mergeTerms($newTerms);
    $termNumbers = $member->terms()->pluck('number')->toArray();

    expect($result)->toBe($member);
    expect($termNumbers)->toEqual([8, 9, 10]);
});
