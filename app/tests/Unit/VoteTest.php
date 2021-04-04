<?php

use App\Document;
use App\Procedure;
use App\Vote;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Vinkla\Hashids\Facades\Hashids;

uses(Tests\TestCase::class, RefreshDatabase::class);

it('uses procedure title for display_title if available', function () {
    $vote = Vote::factory([
        'document_id' => Document::factory([
            'procedure_id' => Procedure::factory([
                'title' => 'Procedure title',
            ]),
        ]),
    ])->make();

    expect($vote->display_title)->toEqual('Procedure title');
});

it('uses document title for display_title if procedure is not available', function () {
    $vote = Vote::factory([
        'document_id' => Document::factory([
            'title' => 'Document title',
            'procedure_id' => null,
        ]),
    ])->make();

    expect($vote->display_title)->toEqual('Document title');
});

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
