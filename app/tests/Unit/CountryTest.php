<?php

use App\Country;
use Illuminate\Database\QueryException;
use Illuminate\Foundation\Testing\RefreshDatabase;

uses(Tests\TestCase::class, RefreshDatabase::class);

it('ensures `code` is unique', function () {
    Country::factory()->createMany([
        ['code' => 'DE'],
        ['code' => 'DE'],
    ]);
})->throws(QueryException::class);
