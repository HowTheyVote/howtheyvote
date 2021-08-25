<?php

use Illuminate\Support\Collection;

uses(Tests\TestCase::class);

it('converts tuples to associative array', function () {
    $collection = new Collection([
        ['a', 1],
        ['b', 2],
        ['c', 3],
    ]);

    $actual = $collection->toAssoc()->toArray();
    $expected = ['a' => 1, 'b' => 2, 'c' => 3];

    expect($actual)->toEqual($expected);
});
