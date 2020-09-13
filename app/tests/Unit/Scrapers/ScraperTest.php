<?php

use App\Member;
use App\Scrapers\Scraper;
use Illuminate\Support\Collection;
use Spatie\Url\Url;

uses(Tests\TestCase::class);

beforeEach(function () {
    $this->scraper = new Scraper;

    Http::fake(function ($request) {
        $path = Url::fromString($request->url())->getPath();

        $fixtures = [
            '/members' => 'members.json',
            '/member_info' => 'member_info.json',
        ];

        $fixture = $fixtures[$path] ?? null;

        if (! $fixture) {
            return Http::response();
        }

        $body = File::get(base_path("tests/data/{$fixture}"));

        return Http::response($body, 200, ['content-type' => 'application/json']);
    });
});

it('uses correct scraper url', function () {
    Scraper::$route = 'members';

    $url = 'http://localhost:5000/members';

    $this->assertEquals($url, $this->scraper->url());
});

it('uses correct scraper url with params', function () {
    Scraper::$route = 'members';
    $this->scraper->params = ['term' => 9];

    $url = 'http://localhost:5000/members?term=9';

    $this->assertEquals($url, $this->scraper->url());
});

it('fetches data', function () {
    Scraper::$route = 'members';
    $data = $this->scraper->run();

    $expected = [
        'web_id' => 12345,
        'first_name' => null,
        'last_name' => null,
        'date_of_birth' => null,
        'terms' => [9],
        'country' => null,
        'group' => null,
    ];

    Http::assertSentCount(1);
    $this->assertCount(1, $this->scraper->data);
    $this->assertEquals($expected, $this->scraper->data[0]);
});

it('converts data to model', function () {
    Scraper::$route = 'member_info';
    Scraper::$model = Member::class;

    $model = $this->scraper->run()->asModel();

    expect($model)->toBeInstanceOf(Member::class);
});

it('converts data to collection', function () {
    Scraper::$route = 'members';
    Scraper::$model = Member::class;

    $collection = $this->scraper->run()->asCollection();

    expect($collection)->toBeInstanceOf(Collection::class);
    expect($collection->first())->toBeInstanceOf(Member::class);
});
