<?php

use App\Enums\CountryEnum;

uses(Tests\TestCase::class);

it('returns the flag', function () {
    expect(CountryEnum::DE->emoji())->toEqual('🇩🇪');
});

it('returns the label', function () {
    expect(CountryEnum::DE->label())->toEqual('Germany');
});
