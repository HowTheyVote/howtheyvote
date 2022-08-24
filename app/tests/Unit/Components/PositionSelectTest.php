<?php

uses(Tests\TestCase::class);

it('renders summary element and radio inputs', function () {
    $view = $this->blade('<x-position-select />');

    expect($view)->toHaveSelectorWithText('summary', text: 'Filter');
});

it('renders radio input and a label for every position', function () {
    $view = $this->blade('<x-position-select />');

    expect($view)->toHaveSelector('details-menu input[type="radio"][value="FOR"]:not([checked])');
    expect($view)->toHaveSelector('details-menu input[type="radio"][value="AGAINST"]:not([checked])');
    expect($view)->toHaveSelector('details-menu input[type="radio"][value="ABSTENTION"]:not([checked])');
    expect($view)->toHaveSelector('details-menu input[type="radio"][value="NOVOTE"]:not([checked])');

    expect($view)->toHaveSelectorWithText('details-menu label[aria-checked="false"] span[data-menu-button-contents]', text: 'FOR');
    expect($view)->toHaveSelectorWithText('details-menu label[aria-checked="false"] span[data-menu-button-contents]', text: 'AGAINST');
    expect($view)->toHaveSelectorWithText('details-menu label[aria-checked="false"] span[data-menu-button-contents]', text: 'ABSTENTION');
    expect($view)->toHaveSelectorWithText('details-menu label[aria-checked="false"] span[data-menu-button-contents]', text: 'NOVOTE');
});

it('pre-checks the default option', function () {
    $view = $this->blade('<x-position-select />');

    expect($view)->toHaveSelector('details-menu input[type="radio"][value=""][checked]');

    // "Show all" is displayed in the options dropdown
    expect($view)->toHaveSelectorWithText('details-menu label[aria-checked="true"]', text: 'Show all');

    // "Filter" is displayed as the button label if the option is selected
    expect($view)->toHaveSelectorWithText('details-menu label[aria-checked="true"] span[data-menu-button-contents]', text: 'Filter');
});

it('optionally adds Alpine.js bindings to inpunts', function () {
    $view = $this->blade('<x-position-select x-model="position" />');
    expect($view)->toHaveSelector('details-menu input[type="radio"][x-model="position"]', count: 5);
});

it('optionally adds `name` attribute to inputs', function () {
    $view = $this->blade('<x-position-select name="position" />');
    expect($view)->toHaveSelector('details-menu input[type="radio"][name="position"]', count: 5);
});

it('has customizable labels', function () {
    $view = $this->blade('<x-position-select label="Click me!!!" reset="Show all!!!" />');

    expect($view)->toHaveSelectorWithText('summary', text: 'Click me!!!');
    expect($view)->toHaveSelectorWithText('details-menu label[aria-checked="true"] span[data-menu-button-contents]', text: 'Click me!!!');
    expect($view)->toHaveSelectorWithText('details-menu label[aria-checked="true"]', text: 'Show all!!! Click me!!!');
});
