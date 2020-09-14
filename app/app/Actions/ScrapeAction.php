<?php

namespace App\Actions;

use Illuminate\Support\Facades\Http;
use Spatie\Url\Url;

class ScrapeAction
{
    private $host;
    private $port;

    public function __construct(string $host, int $port)
    {
        $this->host = $host;
        $this->port = $port;
    }

    public function execute(string $route, array $params): array
    {
        $url = $this->url($route, $params);

        return Http::get($url)->json();
    }

    protected function url(string $route, array $params = []): string
    {
        $url = new Url;
        $url = $url
            ->withScheme('http')
            ->withHost(config('scrapers.host'))
            ->withPort(config('scrapers.port'))
            ->withPath($route);

        foreach ($params as $key => $value) {
            $url = $url->withQueryParameter($key, $value);
        }

        return (string) $url;
    }
}
