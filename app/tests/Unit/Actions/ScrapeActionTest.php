<?php

use App\Actions\ScrapeAction;

uses(Tests\TestCase::class);

beforeEach(function () {
    $this->scrapeAction = $this->app->make(ScrapeAction::class);
});

it('uses correct scraper url', function () {
    $url = 'http://localhost:5000/members';
    expect($this->scrapeAction->url('members'))->toEqual($url);
});

it('uses correct scraper url with params', function () {
    $url = 'http://localhost:5000/members?term=9';
    expect($this->scrapeAction->url('members', ['term' => 9]))->toEqual($url);
});

it('fetches data', function () {
    Http::fakeJsonFromFile('*', 'members.json');

    $expected = [
        'web_id' => 12345,
        'terms' => [9],
    ];

    $data = $this->scrapeAction->execute('members', ['term' => 9]);

    Http::assertSentCount(1);
    expect($data)->toHaveCount(1);
    expect($data[0])->toEqual($expected);
});
