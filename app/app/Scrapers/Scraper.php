<?php

namespace App\Scrapers;

use Illuminate\Support\Facades\Http;
use Illuminate\Http\Client\Response;
use Spatie\Url\Url;
use Spatie\Url\QueryParameterBag;

class Scraper
{
    static public string $route = '';

    public array $params = [];

    public array $data = [];

    public function __construct(array $params = []) {
        $this->params = $params;
    }

    public function run(): void
    {
        $response = Http::get($this->url());
        $this->data = $response->json();
    }

    public function url(): string
    {
        $url = new Url;
        $url = $url
            ->withScheme('http')
            ->withHost(config('scrapers.host'))
            ->withPort(config('scrapers.port'))
            ->withPath(self::$route);

        foreach($this->params as $key => $value) {
            $url = $url->withQueryParameter($key, $value);
        }

        return (string) $url;
    }
}
