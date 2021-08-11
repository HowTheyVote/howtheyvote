<?php

use App\Session;

uses(Tests\TestCase::class);

it('has a display title', function () {
    $session = Session::make([
        'start_date' => '2021-08-11',
        'end_date' => '2021-08-15',
    ]);

    expect($session->display_title)->toEqual('Session from 2021-08-11 to 2021-08-15');
});
