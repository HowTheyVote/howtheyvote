<?php

use Illuminate\Support\Str;

uses(Tests\TestCase::class);

it('obfuscates strings using html entities', function () {
    expect(Str::obfuscate('test'))->toEqual('&#x74;&#x65;&#x73;&#x74;');
});
