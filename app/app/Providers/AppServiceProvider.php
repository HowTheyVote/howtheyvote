<?php

namespace App\Providers;

use App\Actions\ScrapeAction;
use Illuminate\Support\Collection;
use Illuminate\Support\Facades\File;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\ServiceProvider;

class AppServiceProvider extends ServiceProvider
{
    /**
     * Register any application services.
     *
     * @return void
     */
    public function register()
    {
        $this->app->bind(ScrapeAction::class, function () {
            return new ScrapeAction(
                config('scrapers.host'),
                config('scrapers.port')
            );
        });
    }

    /**
     * Bootstrap any application services.
     *
     * @return void
     */
    public function boot()
    {
        Http::macro('jsonResponseFromFile', function (string $path) {
            $body = File::get(base_path("tests/data/{$path}"));

            return Http::response($body, 200, [
                'content-type' => 'application/json',
            ]);
        });

        Http::macro('fakeJsonFromFile', function (string $url, string $fixture) {
            return Http::fake([
                $url => Http::jsonResponseFromFile($fixture),
            ]);
        });

        // DB::listen(function ($query) {
        //     Log::info(
        //         $query->sql,
        //         $query->bindings,
        //         $query->time
        //     );
        // });

        Collection::macro('toAssoc', function () {
            return $this->reduce(function ($assoc, $keyValuePair) {
                [$key, $value] = $keyValuePair;
                $assoc[$key] = $value;

                return $assoc;
            }, new static);
        });
    }
}
