<?php

use App\Scrapers\Scraper;

uses(Tests\TestCase::class);

beforeEach(function () {
    Scraper::$route = 'members';
    $this->scraper = new Scraper;

    Http::fake([
        'http://localhost:5000/members' => Http::response([
            [
                'ep_web_id' => 12345,
                'first_name' => 'John',
                'last_name' => 'Doe',
                'date_of_birth' => '1975-01-01',
            ],
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
        'first_name' => 'John',
        'last_name' => 'Doe',
        'date_of_birth' => '1975-01-01',
    ];

    Http::assertSentCount(1);
    $this->assertCount(1, $this->scraper->data);
    $this->assertEquals($expected, $this->scraper->data[0]);
});
