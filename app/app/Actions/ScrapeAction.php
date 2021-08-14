<?php

namespace App\Actions;

use App\Exceptions\ScrapingException;
use Illuminate\Support\Facades\Http;
use Spatie\Url\Url;

class ScrapeAction extends Action
{
    private $host;
    private $port;

    public function __construct(string $host, int $port)
    {
        $this->host = $host;
        $this->port = $port;
    }

    public function execute(string $route, array $params): mixed
    {
        $url = $this->url($route, $params);
        $this->log("Fetching {$url}");
        $response = Http::get($url);

        if ($response->status() !== 200) {
            throw new ScrapingException($route, $params);
        }

        return $response->json();
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
