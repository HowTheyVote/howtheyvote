<?php

namespace App\Providers;

use App\Actions\ScrapeAction;
use App\Actions\ScrapeAndSaveMembersAction;
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

        $this->app->bind(ScrapeAndSaveMembersAction::class);
        $this->app->bind(ScrapeAndSaveMemberInfoAction::class);
    }

    /**
     * Bootstrap any application services.
     *
     * @return void
     */
    public function boot()
    {
        Http::macro('fakeJsonFromFile', function (string $url, string $fixture) {
            $body = File::get(base_path("tests/data/{$fixture}"));
            $response = Http::response($body, 200, [
                'content-type' => 'application/json',
            ]);

            return Http::stubUrl($url, $response);
        });
    }
}
