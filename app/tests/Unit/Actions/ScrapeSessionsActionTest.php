<?php

use App\Actions\ScrapeSessionsAction;
use App\Enums\LocationEnum;
use App\Session;
use Illuminate\Foundation\Testing\RefreshDatabase;

uses(Tests\TestCase::class, RefreshDatabase::class);

beforeEach(function () {
    $this->action = $this->app->make(ScrapeSessionsAction::class);

    Http::fakeJsonFromFile('*/sessions?year=2021&month=11', 'sessions.json');
});

it('creates new session records', function () {
    $this->action->execute(2021, 11);

    expect(Session::count())->toEqual(2);

    $session = Session::find(1);

    expect($session->start_date)->toEqual('2021-11-10');
    expect($session->end_date)->toEqual('2021-11-11');
    expect($session->location)->toEqual(LocationEnum::BRUSSELS());

    $session = Session::find(2);

    expect($session->start_date)->toEqual('2021-11-22');
    expect($session->end_date)->toEqual('2021-11-25');
    expect($session->location)->toEqual(LocationEnum::STRASBOURG());
});

it('updates existing session records when scraping repeatedly', function () {
    Session::factory([
        'start_date' => '2021-11-10',
        'end_date' => '2021-11-11',
        'location' => LocationEnum::STRASBOURG(),
    ])->make();

    $this->action->execute(2021, 11);

    expect(Session::count())->toEqual(2);

    $session = Session::first();
    expect($session->location)->toEqual(LocationEnum::BRUSSELS());
    expect($session->start_date)->toEqual('2021-11-10');
});
