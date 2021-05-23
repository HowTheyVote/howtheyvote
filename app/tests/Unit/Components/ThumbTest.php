<?php

use App\Enums\VotePositionEnum;
use App\Enums\VoteResultEnum;

uses(Tests\TestCase::class);

it('accepts and maps result enums', function () {
    $view = $this->blade('<x-thumb :result="$result" />', ['result' => VoteResultEnum::ADOPTED()]);
    expect($view)->toSee('thumb--adopted');

    $view = $this->blade('<x-thumb :result="$result" />', ['result' => VoteResultEnum::REJECTED()]);
    expect($view)->toSee('thumb--rejected');
});

it('accepts and maps result string', function () {
    $view = $this->blade('<x-thumb result="adopted" />');
    expect($view)->toSee('thumb--adopted');

    $view = $this->blade('<x-thumb result="rejected" />');
    expect($view)->toSee('thumb--rejected');
});

it('accepts and maps position enums', function () {
    $view = $this->blade('<x-thumb :position="$position" />', ['position' => VotePositionEnum::FOR()]);
    expect($view)->toSee('thumb--for');

    $view = $this->blade('<x-thumb :position="$position" />', ['position' => VotePositionEnum::AGAINST()]);
    expect($view)->toSee('thumb--against');

    $view = $this->blade('<x-thumb :position="$position" />', ['position' => VotePositionEnum::ABSTENTION()]);
    expect($view)->toSee('thumb--abstention');
});

it('accepts and maps position strings', function () {
    $view = $this->blade('<x-thumb position="for" />');
    expect($view)->toSee('thumb--for');

    $view = $this->blade('<x-thumb result="against" />');
    expect($view)->toSee('thumb--against');

    $view = $this->blade('<x-thumb position="abstention" />');
    expect($view)->toSee('thumb--abstention');
});

it('accepts circle as a style modifier', function () {
    $view = $this->blade('<x-thumb position="for" style="circle" />');
    expect($view)->toSee('thumb--circle');
});
