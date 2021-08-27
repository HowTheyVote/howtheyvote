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

it('filters falsy modifiers', function () {
    $bag = new ComponentAttributeBag();
    $actual = $bag->bem('button', ['', null, false, 'large'])->getAttributes();
    $expected = ['class' => 'button button--large'];

    expect($actual)->toEqual($expected);
});

it('appends modifier if constraint is true', function () {
    $bag = new ComponentAttributeBag();
    $expected = ['class' => 'button button--large'];
    $actual = $bag->bem('button', [
        'large' => true,
        'pink' => false,
    ])->getAttributes();

    expect($actual)->toEqual($expected);
});
