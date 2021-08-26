<?php

namespace App\Providers;

use App\Actions\ScrapeAction;
use App\Mixins\CollectionMixin;
use App\Mixins\ComponentAttributeBagMixin;
use App\Mixins\StrMixin;
use App\Mixins\TestResponseMixin;
use App\Mixins\TestViewMixin;
use Illuminate\Support\Collection;
use Illuminate\Support\Facades\File;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\ServiceProvider;
use Illuminate\Support\Str;
use Illuminate\Testing\TestResponse;
use Illuminate\Testing\TestView;
use Illuminate\View\ComponentAttributeBag;

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

        Collection::mixin(new CollectionMixin);
        ComponentAttributeBag::mixin(new ComponentAttributeBagMixin);
        Str::mixin(new StrMixin);
        TestView::mixin(new TestViewMixin);
        TestResponse::mixin(new TestResponseMixin);
    }
}
