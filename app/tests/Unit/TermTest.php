<?php

use App\Term;
use Illuminate\Database\QueryException;
use Illuminate\Foundation\Testing\RefreshDatabase;

uses(Tests\TestCase::class, RefreshDatabase::class);

it('ensures `number` is unique', function () {
    Term::factory()->createMany([
        ['number' => 9],
        ['number' => 9],
    ]);
})->throws(QueryException::class);
