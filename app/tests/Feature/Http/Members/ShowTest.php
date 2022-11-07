<?php

use App\Enums\CountryEnum;
use App\Group;
use App\Member;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Support\Carbon;
use Illuminate\Support\Facades\Storage;

uses(Tests\TestCase::class, RefreshDatabase::class);

beforeEach(function () {
    $this->firstJan = new Carbon('2020-01-01');
    $this->thirdJan = new Carbon('2020-01-03');
    Carbon::setTestNow($this->thirdJan);

    $greens = Group::factory([
        'code' => 'GREENS',
        'name' => 'Greens/European Free Alliance',
        'abbreviation' => 'Greens/EFA',
    ])->create();

    $this->member = Member::factory([
        'first_name' => 'Jane',
        'last_name' => 'DOE',
        'country' => CountryEnum::NL(),
        'twitter' => '@handle',
    ])->activeAt($this->firstJan, $greens)
        ->activeAt($this->thirdJan, $greens)
        ->create();

    $this->memberId = Member::first()->id;
});

afterEach(function () {
    Carbon::setTestNow();
});

it('renders successfully', function () {
    $response = $this->get("/members/{$this->memberId}");
    expect($response)->toHaveStatus(200);
});

it('shows a placeholder when no profile picture is found', function () {
    Storage::fake('public');

    $response = $this->get("/members/{$this->memberId}");
    expect($response)->toHaveSelector("img[src$='assets/placeholder.svg']");
});

it('shows an info box with contact links for active members', function () {
    Storage::fake('public');
    Storage::disk('public')->put("members/{$this->member->id}.jpg", 'fake');

    $response = $this->get("/members/{$this->memberId}");

    expect($response)->toHaveSelector("img[src$='/members/{$this->memberId}.jpg']");
    expect($response)->toHaveSelectorWithText('.member-header', 'Greens/European Free Alliance');
    expect($response)->toHaveSelectorWithText('.member-header', 'Netherlands');

    expect($response)->toHaveSelectorWithText('.member-header', 'Twitter');
    expect($response)->not()->toHaveSelectorWithText('member-header', 'Facebook');
});

it('shows contact info for non-active members', function () {
    Carbon::setTestNow();

    Storage::fake('public');
    Storage::disk('public')->put("members/{$this->member->id}.jpg", 'fake');

    $response = $this->get("/members/{$this->memberId}");

    expect($response)->toHaveSelector("img[src$='/members/{$this->memberId}.jpg']");
    expect($response)->toHaveSelectorWithText('.member-header', 'Netherlands');
    expect($response)->toHaveSelectorWithText('.member-header', 'Twitter');
    expect($response)->not()->toHaveSelectorWithText('.member-header', 'Facebook');
});
