<?php

uses(Tests\TestCase::class);

beforeEach(function () {
    $props = [
        'stats' => [
            'voted' => 90,
            'active' => 100,
            'by_position' => [
                'FOR' => 60,
                'AGAINST'=> 20,
                'ABSTENTION'=> 10,
            ],
        ],
    ];

    $this->view = $this->blade('<x-vote-result-chart :stats=$stats />', $props);
});

it('renders three bars', function () {
    expect($this->view)->toSeeInOrder([
        'vote-result-chart__bar--for',
        'vote-result-chart__bar--against',
        'vote-result-chart__bar--abstention',
    ]);
});

it('displays absolute numbers correctly', function () {
    expect($this->view)->toSeeText('For: 60');
    expect($this->view)->toSeeText('Against: 20');
    expect($this->view)->toSeeText('Abstentions: 10');
    expect($this->view)->toSeeText('90 MEPs voted');
    expect($this->view)->toSeeText('10 MEPs didn’t vote');
});
