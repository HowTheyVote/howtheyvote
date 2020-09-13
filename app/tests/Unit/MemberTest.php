<?php

use App\Member;

uses(Tests\TestCase::class);

it('converts date_of_birth to date object', function () {
    $member = new Member([
        'date_of_birth' => '1975-01-01',
    ]);

    expect($member->date_of_birth)->toBeInstanceOf(DateTime::class);
});
