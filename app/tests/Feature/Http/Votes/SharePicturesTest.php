<?php

use App\Vote;
use Illuminate\Foundation\Testing\RefreshDatabase;

uses(Tests\TestCase::class, RefreshDatabase::class);

it('renders successfully', function () {
    $vote = Vote::factory()->withStats()->create();
    $response = $this->get("/votes/{$vote->id}/share-picture");

    expect($response)->toHaveStatus(200);
});
