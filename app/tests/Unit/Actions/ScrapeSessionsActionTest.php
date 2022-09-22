<?php

use App\Actions\ScrapeSessionsAction;
use App\Enums\LocationEnum;
use App\Session;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Support\Carbon;

uses(Tests\TestCase::class, RefreshDatabase::class);

beforeEach(function () {
    $this->action = $this->app->make(ScrapeSessionsAction::class);

    Http::fakeJsonFromFile('*/sessions_obs?year=2021&month=11', 'sessions_obs.json');
    Http::fakeJsonFromFile('*/sessions_parl?term=9&year=2021&month=11', 'sessions_parl.json');
});

it('creates new session records', function () {
    $this->action->execute(9, 2021, 11);

    expect(Session::count())->toEqual(3);

    $session = Session::find(1);

    expect($session->start_date)->toEqual(Carbon::create('2021-11-02'));
    expect($session->end_date)->toEqual(Carbon::create('2021-11-04'));
    expect($session->location)->toEqual(LocationEnum::NONE);

    $session = Session::find(2);

    expect($session->start_date)->toEqual(Carbon::create('2021-11-10'));
    expect($session->end_date)->toEqual(Carbon::create('2021-11-11'));
    expect($session->location)->toEqual(LocationEnum::BRUSSELS);

    $session = Session::find(3);

    expect($session->start_date)->toEqual(Carbon::create('2021-11-22'));
    expect($session->end_date)->toEqual(Carbon::create('2021-11-25'));
    expect($session->location)->toEqual(LocationEnum::STRASBOURG);
});

it('updates existing session records when scraping repeatedly', function () {
    Session::factory([
        'start_date' => '2021-11-10',
        'end_date' => '2021-11-11',
        'location' => LocationEnum::STRASBOURG,
    ])->create();

    $id = Session::all()->first()->id;

    $this->action->execute(9, 2021, 11);

    expect(Session::count())->toEqual(3);

    $session = Session::find($id);

    expect($session->location)->toEqual(LocationEnum::BRUSSELS);
    expect($session->start_date)->toEqual(Carbon::create('2021-11-10'));
});
