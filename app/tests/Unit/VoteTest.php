<?php

use App\Vote;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Vinkla\Hashids\Facades\Hashids;

uses(Tests\TestCase::class, RefreshDatabase::class);

it('uses vote description for display_title if document is not available', function () {
    $vote = Vote::factory([
        'description' => 'Vote description',
        'document_id' => null,
    ])->make();

    expect($vote->display_title)->toEqual('Vote description');
});

it('has a hash id', function () {
    $vote = Vote::factory(['id' => 1])->make();

    $expected = Hashids::encode(1);
    expect($vote->hash_id)->toEqual($expected);
});
