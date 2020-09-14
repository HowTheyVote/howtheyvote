<?php

use App\Actions\ScrapeAction;

uses(Tests\TestCase::class);

it('fetches data', function () {
    $this->action = $this->app->make(ScrapeAction::class);
    Http::fakeJsonFromFile('*/hello?name=John', 'hello.json');

    $data = $this->action->execute('hello', ['name' => 'John']);

    Http::assertSentCount(1);
    expect($data)->toEqual(['message' => 'Hello John!']);
});
