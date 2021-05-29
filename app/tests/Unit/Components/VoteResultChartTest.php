<?php

use App\VotingList;

uses(Tests\TestCase::class);

beforeEach(function () {
    $stats = VotingList::factory()->withStats()->make()->stats;
    $this->view = $this->blade('<x-vote-result-chart :stats=$stats />', ['stats' => $stats]);
});

it('renders three bars', function () {
    expect($this->view)->toSeeInOrder([
        'vote-result-chart__bar--for',
        'vote-result-chart__bar--against',
        'vote-result-chart__bar--abstention',
    ]);
});

it('displays absolute numbers correctly', function () {
    expect($this->view)->toSeeText('For: 10');
    expect($this->view)->toSeeText('Against: 20');
    expect($this->view)->toSeeText('Abstentions: 30');
    expect($this->view)->toSeeText('60 MEPs voted');
    expect($this->view)->toSeeText('40 MEPs didn’t vote');
});
