<?php

use App\Actions\ScrapeAction;
use App\Exceptions\ScrapingException;

uses(Tests\TestCase::class);

it('fetches data', function () {
    $this->action = $this->app->make(ScrapeAction::class);
    Http::fakeJsonFromFile('*/hello?name=John', 'hello.json');

    $data = $this->action->execute('hello', ['name' => 'John']);

    Http::assertSentCount(1);
    expect($data)->toEqual(['message' => 'Hello John!']);
});

it('throws exception', function () {
    $this->action = $this->app->make(ScrapeAction::class);
    Http::fake(['*/hello?name=John' => Http::response('', 500)]);
    $this->action->execute('hello', ['name' => 'John']);
})->throws(ScrapingException::class);
