<?php

use App\Member;
use Illuminate\Foundation\Testing\RefreshDatabase;

uses(Tests\TestCase::class, RefreshDatabase::class);

beforeEach(function () {
    $this->member = Member::factory()->create();
});

it('renders successfully', function () {
    $response = $this->get("/members/{$this->member->id}");
    expect($response)->toHaveStatus(200);
});
