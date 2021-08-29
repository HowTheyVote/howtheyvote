<?php

uses(Tests\TestCase::class);

it('renders markdown contents', function () {
    $response = $this->get('/pages/about');

    expect($response)->toHaveStatus(200);
    expect($response)->toHaveSelectorWithText('h1', 'About');
    expect($response)->toHaveSelectorWithText('h2', 'Contact Us');
});

it('returns 404 if page does not exist', function () {
    $response = $this->get('/pages/404');

    expect($response)->toHaveStatus(404);
});
