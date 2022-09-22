<?php

use App\Enums\VotePositionEnum;
use App\Enums\VoteResultEnum;

uses(Tests\TestCase::class);

it('accepts and maps result enums', function () {
    $view = $this->blade('<x-thumb :result="$result" />', ['result' => VoteResultEnum::ADOPTED]);
    expect($view)->toHaveSelector('.thumb--adopted');

    $view = $this->blade('<x-thumb :result="$result" />', ['result' => VoteResultEnum::REJECTED]);
    expect($view)->toHaveSelector('.thumb--rejected');
});

it('accepts and maps result string', function () {
    $view = $this->blade('<x-thumb result="adopted" />');
    expect($view)->toHaveSelector('.thumb--adopted');

    $view = $this->blade('<x-thumb result="rejected" />');
    expect($view)->toHaveSelector('.thumb--rejected');
});

it('accepts and maps position enums', function () {
    $view = $this->blade('<x-thumb :position="$position" />', ['position' => VotePositionEnum::FOR]);
    expect($view)->toHaveSelector('.thumb--for');

    $view = $this->blade('<x-thumb :position="$position" />', ['position' => VotePositionEnum::AGAINST]);
    expect($view)->toHaveSelector('.thumb--against');

    $view = $this->blade('<x-thumb :position="$position" />', ['position' => VotePositionEnum::ABSTENTION]);
    expect($view)->toHaveSelector('.thumb--abstention');
});

it('accepts and maps position strings', function () {
    $view = $this->blade('<x-thumb position="for" />');
    expect($view)->toHaveSelector('.thumb--for');

    $view = $this->blade('<x-thumb result="against" />');
    expect($view)->toHaveSelector('.thumb--against');

    $view = $this->blade('<x-thumb position="abstention" />');
    expect($view)->toHaveSelector('.thumb--abstention');
});

it('accepts circle as a style modifier', function () {
    $view = $this->blade('<x-thumb position="for" style="circle" />');
    expect($view)->toHaveSelector('.thumb--circle');
});
