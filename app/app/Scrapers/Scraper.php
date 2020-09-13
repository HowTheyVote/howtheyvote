<?php

namespace App\Scrapers;

use Illuminate\Support\Collection;
use Illuminate\Support\Facades\Http;
use Spatie\Url\Url;

class Scraper
{
    public static string $route = '';

    public array $params = [];

    public array $data = [];

    public static string $model;

    public function __construct(array $params = [])
    {
        $this->params = $params;
    }

    public function run(): self
    {
        $response = Http::get($this->url());
        $this->data = $response->json();

        return $this;
    }

    public function url(): string
    {
        $url = new Url;
        $url = $url
            ->withScheme('http')
            ->withHost(config('scrapers.host'))
            ->withPort(config('scrapers.port'))
            ->withPath(self::$route);

        foreach ($this->params as $key => $value) {
            $url = $url->withQueryParameter($key, $value);
        }

        return (string) $url;
    }

    public function asModel(): object
    {
        return self::convertDataToModel($this->data);
    }

    public function asCollection(): Collection
    {
        return collect($this->data)->map(function ($data) {
            return self::convertDataToModel($data);
        });
    }

    protected static function convertDataToModel(array $data): object
    {
        return new self::$model($data);
    }
}
