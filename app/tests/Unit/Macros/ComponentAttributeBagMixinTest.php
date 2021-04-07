<?php

use Illuminate\View\ComponentAttributeBag;

uses(Tests\TestCase::class);

it('appends BEM-style classes', function () {
    $bag = new ComponentAttributeBag();
    $actual = $bag->bem('button', 'large primary')->getAttributes();
    $expected = ['class' => 'button button--large button--primary'];

    expect($actual)->toEqual($expected);
});

it('accepts no modifier', function () {
    $bag = new ComponentAttributeBag();
    $actual = $bag->bem('button')->getAttributes();
    $expected = ['class' => 'button'];

    expect($actual)->toEqual($expected);
});
