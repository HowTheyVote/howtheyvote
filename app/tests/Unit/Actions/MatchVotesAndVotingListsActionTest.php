<?php

use App\Actions\MatchVotesAndVotingListsAction;
use App\Enums\VoteTypeEnum;
use App\Vote;
use App\VoteCollection;
use App\VotingList;
use Illuminate\Foundation\Testing\RefreshDatabase;

uses(Tests\TestCase::class, RefreshDatabase::class);

beforeEach(function () {
    $this->action = $this->app->make(MatchVotesAndVotingListsAction::class);

    $this->voteCollection = VoteCollection::factory([
        'reference' => 'A9-0123/2021',
    ])->create();
});

it('matches vote with title', function () {
    $vote = Vote::factory([
        'type' => VoteTypeEnum::AMENDMENT(),
        'vote_collection_id' => $this->voteCollection->id,
        'formatted' => 'Am 1/2',
    ])->create();

    $votingList = VotingList::factory([
        'description' => 'Quelques textes en français - Some English text - Irgendein deutscher Text - A9-0123/2021 - Name of rapporteur - Am 1/2',
        'reference' => 'A9-0123/2021',
    ])->create();

    $this->action->execute();

    expect($votingList->fresh()->vote->id)->toEqual($vote->id);
});

it('matches vote without title', function () {
    $vote = Vote::factory([
        'type' => VoteTypeEnum::AMENDMENT(),
        'vote_collection_id' => $this->voteCollection->id,
        'formatted' => 'Am 1/2',
    ])->create();

    $votingList = VotingList::factory([
        'description' => 'A9-0123/2021 - Name of rapporteur - Am 1/2',
        'reference' => 'A9-0123/2021',
    ])->create();

    $this->action->execute();

    expect($votingList->fresh()->vote->id)->toEqual($vote->id);
});
