<?php

uses(Tests\TestCase::class);

it('contains correct percentage value', function () {
    $view = $this->blade('<x-vote-result-chart-bar :value="10" :total="100" position="for" />');
    expect($view)->toSeeText('10%');
});

it('shows the correct thumb', function () {
    $view = $this->blade('<x-vote-result-chart-bar :value="10" :total="100" position="for" />');
    expect($view)->toHaveSelector('.thumb--for');

    $view = $this->blade('<x-vote-result-chart-bar :value="10" :total="100" position="against" />');
    expect($view)->toHaveSelector('.thumb--against');

    $view = $this->blade('<x-vote-result-chart-bar :value="10" :total="100" position="abstention" />');
    expect($view)->toHaveSelector('.thumb--abstention');
});

it('appends medium modifier if percentage is below 15', function () {
    $view = $this->blade('<x-vote-result-chart-bar :value="14" :total="100" position="for" />');
    expect($view)->toHaveSelector('.vote-result-chart__bar--medium');
    expect($view)->not()->toHaveSelector('.vote-result-chart__bar--small');
});

it('appends small modifier if percentage is below 10', function () {
    $view = $this->blade('<x-vote-result-chart-bar :value="9" :total="100" position="for" />');
    expect($view)->toHaveSelector('.vote-result-chart__bar--small');
    expect($view)->not()->toHaveSelector('.vote-result-chart__bar--medium');
});

it('has the correct width depending on its percentage value', function () {
    $view = $this->blade('<x-vote-result-chart-bar :value="10" :total="100" position="for" />');
    expect($view)->toHaveSelector('.vote-result-chart__bar[style="--ratio: 0.1"]');
});
