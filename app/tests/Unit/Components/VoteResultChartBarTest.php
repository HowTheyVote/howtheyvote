<?php

uses(Tests\TestCase::class);

it('contains correct percentage value', function () {
    $view = $this->blade('<x-vote-result-chart-bar :value="10" :total="100" position="for" />');
    expect($view)->toSeeText('10%');
});

it('contains no percentage value if it would be below 5%', function () {
    $view = $this->blade('<x-vote-result-chart-bar :value="4" :total="100" position="for" />');
    expect($view)->not()->toSeeText('4%');
});

it('shows the correct thumb', function () {
    $view = $this->blade('<x-vote-result-chart-bar :value="10" :total="100" position="for" />');
    expect($view)->toHaveSelector('.thumb--for');

    $view = $this->blade('<x-vote-result-chart-bar :value="10" :total="100" position="against" />');
    expect($view)->toHaveSelector('.thumb--against');

    $view = $this->blade('<x-vote-result-chart-bar :value="10" :total="100" position="abstention" />');
    expect($view)->toHaveSelector('.thumb--abstention');
});

it('shows no thumb if percentage is below 10', function () {
    $view = $this->blade('<x-vote-result-chart-bar :value="9" :total="100" position="for" />');
    expect($view)->not()->toHaveSelector('.thumb');
});

it('has the correct width depending on its percentage value', function () {
    $view = $this->blade('<x-vote-result-chart-bar :value="10" :total="100" position="for" />');
    expect($view)->toHaveSelector('.vote-result-chart__bar[style="--ratio: 0.1"]');
});
