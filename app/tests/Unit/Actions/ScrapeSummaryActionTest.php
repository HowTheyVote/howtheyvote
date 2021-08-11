<?php

use App\Actions\ScrapeSummaryAction;
use App\Summary;
use App\VoteCollection;
use Illuminate\Foundation\Testing\RefreshDatabase;

uses(Tests\TestCase::class, RefreshDatabase::class);

it('creates summary record', function () {
    $this->action = $this->app->make(ScrapeSummaryAction::class);

    Http::fakeJsonFromFile('*/summary_id?reference=B9-0116%2F2021', 'summary_id.json');
    Http::fakeJsonFromFile('*/summary?summary_id=1234567', 'summary.json');

    $voteCollection = VoteCollection::factory([
        'reference' => 'B9-0116/2021',
    ])->make();

    $this->action->execute($voteCollection);

    $summary = Summary::firstWhere('reference', 'B9-0116/2021');

    expect($summary->reference)->toEqual('B9-0116/2021');
    expect($summary->text)->toEqual('Summary of the adopted text');
});
