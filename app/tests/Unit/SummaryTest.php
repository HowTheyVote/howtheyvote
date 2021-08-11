<?php

use App\Summary;
use Illuminate\Foundation\Testing\RefreshDatabase;

uses(Tests\TestCase::class, RefreshDatabase::class);

it('has excerpt', function () {
    $summary = Summary::factory([
        'text' => "The European Parliament adopted by 667 votes to 1, with 27 abstentions, a resolution on the situation in Myanmar.\n\nThe text adopted in plenary had been tabled as a joint resolution by the EPP, S&D, Renew, Greens/EFA, ECR groups and The Left.\n\nOn 1 February 2021, the military of Myanmar, known as the Tatmadaw, in a clear violation of the constitution of Myanmar, arrested President Win Myint and State Counsellor Aung San Suu Kyi, as well as leading members of the government, seized power over the legislative, judicial and executive branches of government through a coup d’état, and issued a one-year state of emergency.",
    ])->make();

    $expected = "The text adopted in plenary had been tabled as a joint resolution by the EPP, S&D, Renew, Greens/EFA, ECR groups and The Left.\n\nOn 1 February 2021, the military of Myanmar, known as the Tatmadaw, in a clear violation of the constitution of Myanmar, arrested President Win Myint and State...";

    expect($summary->excerpt)->toEqual($expected);
});

it('removes headings from excerpt', function () {
    $summary = Summary::factory([
        'text' => implode("\n\n", [
            'First paragraph is always removed',
            '## Heading',
            'Second paragraph',
        ]),
    ])->make();

    expect($summary->excerpt)->toEqual('Second paragraph');
})->only();
