<?php

uses(Tests\TestCase::class);

it('renders a tag if href is given', function () {
    $view = $this->blade('<x-button href="https://howtheyvote.eu" />');
    expect($view)->toHaveSelector('a[href="https://howtheyvote.eu"]');
});

it('render button tag if href is not given', function () {
    $view = $this->blade('<x-button />');
    expect($view)->toHaveSelector('button');
});
