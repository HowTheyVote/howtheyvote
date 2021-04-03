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
    expect($view)->toSee('thumb--for');

    $view = $this->blade('<x-vote-result-chart-bar :value="10" :total="100" position="against" />');
    expect($view)->toSee('thumb--against');

    $view = $this->blade('<x-vote-result-chart-bar :value="10" :total="100" position="abstention" />');
    expect($view)->toSee('thumb--abstention');
});

it('shows no thumb if percentage is below 10', function () {
    $view = $this->blade('<x-vote-result-chart-bar :value="9" :total="100" position="for" />');
    expect($view)->not()->toSee('thumb');
});

it('has the correct width depending on its percentage value', function () {
    $view = $this->blade('<x-vote-result-chart-bar :value="10" :total="100" position="for" />');
    expect($view)->toSee('--ratio: 0.1');
});
