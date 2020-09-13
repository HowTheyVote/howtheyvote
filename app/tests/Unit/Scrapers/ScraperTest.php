<?php

use App\Member;
use App\Scrapers\Scraper;
use Illuminate\Support\Collection;

uses(Tests\TestCase::class);

beforeEach(function () {
    Scraper::$route = 'members';
    $this->scraper = new Scraper;

    Http::fake([
        'http://localhost:5000/members' => Http::response([
            [
                'ep_web_id' => 12345,
                'first_name' => null,
                'last_name' => null,
                'date_of_birth' => null,
            ],
        ]),
        'http://localhost:5000/member_info' => Http::response([
            'ep_web_id' => 12345,
            'first_name' => 'John',
            'last_name' => 'Doe',
            'date_of_birth' => '1975-01-01',
        ]),
    ]);
});

it('uses correct scraper url', function () {
    $url = 'http://localhost:5000/members';
    $this->assertEquals($url, $this->scraper->url());
});

it('uses correct scraper url with params', function () {
    $this->scraper->params = ['term' => 9];
    $url = 'http://localhost:5000/members?term=9';
    $this->assertEquals($url, $this->scraper->url());
});

it('fetches data', function () {
    $data = $this->scraper->run();

    $expected = [
        'ep_web_id' => 12345,
        'first_name' => null,
        'last_name' => null,
        'date_of_birth' => null,
    ];

    Http::assertSentCount(1);
    $this->assertCount(1, $this->scraper->data);
    $this->assertEquals($expected, $this->scraper->data[0]);
});

it('converts data to model', function () {
    Scraper::$route = 'member_info';
    Scraper::$model = Member::class;

    $data = $this->scraper->run();
    $model = $this->scraper->asModel();

    expect($model)->toBeInstanceOf(Member::class);
});

it('converts data to collection', function () {
    Scraper::$route = 'members';
    Scraper::$model = Member::class;

    $data = $this->scraper->run();
    $collection = $this->scraper->asCollection();

    expect($collection)->toBeInstanceOf(Collection::class);
    expect($collection->first())->toBeInstanceOf(Member::class);
});
