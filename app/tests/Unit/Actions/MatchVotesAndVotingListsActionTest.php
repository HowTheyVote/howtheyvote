<?php

use App\Actions\MatchVotesAndVotingListsAction;
use App\Enums\VoteTypeEnum;
use App\Exceptions\CouldNotMatchVoteException;
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
        'remarks' => '102030',
    ])->create();

    $votingList = VotingList::factory([
        'description' => 'Quelques textes en français - Some English text - Irgendein deutscher Text - A9-0123/2021 - Name of rapporteur - Am 1/2',
        'reference' => 'A9-0123/2021',
    ])->withStats(10, 20, 30)->create();

    $this->action->execute();

    expect($votingList->fresh()->vote->id)->toEqual($vote->id);
});

it('matches vote without title', function () {
    $vote = Vote::factory([
        'type' => VoteTypeEnum::AMENDMENT(),
        'vote_collection_id' => $this->voteCollection->id,
        'formatted' => 'Am 1/2',
        'remarks' => '102030',
    ])->create();

    $votingList = VotingList::factory([
        'description' => 'A9-0123/2021 - Name of rapporteur - Am 1/2',
        'reference' => 'A9-0123/2021',
    ])->withStats(10, 20, 30)->create();

    $this->action->execute();

    expect($votingList->fresh()->vote->id)->toEqual($vote->id);
});

it('matches based on vote reference', function () {
    $vote = Vote::factory([
        'vote_collection_id' => $this->voteCollection->id,
        'reference' => 'B9-4567/2021',
        'formatted' => 'Am 1/2',
        'remarks' => '102030',
    ])->create();

    $votingList = VotingList::factory([
        'description' => 'B9-4567/2021 - Name of rapporteur - Am 1/2',
        'reference' => 'B9-4567/2021',
    ])->withStats(10, 20, 30)->create();

    $this->action->execute();

    expect($votingList->fresh()->vote->id)->toEqual($vote->id);
});

it('throws an error when a vote is present but no voting list', function () {
    $vote = Vote::factory(['id' => 1])->create();

    $this->action->execute();
})->throws(CouldNotMatchVoteException::class, 'No voting list for vote 1 found.');

it('throws an error when a vote has multiple matching voting lists', function () {
    $vote = Vote::factory([
        'id' => 1,
        'vote_collection_id' => $this->voteCollection->id,
        'formatted' => 'Am 1/2',
        'type' => VoteTypeEnum::AMENDMENT(),
    ])->create();

    VotingList::factory([
        'description' => 'A9-0123/2021 - Name of rapporteur - Am 1/2',
        'reference' => 'A9-0123/2021',
    ])->count(2)->create();

    $this->action->execute();
})->throws(CouldNotMatchVoteException::class, 'Multiple voting lists for vote 1 found.');

it('throws an error when a vote and its matched voting list have different results', function () {
    $vote = Vote::factory([
        'id' => 1,
        'vote_collection_id' => $this->voteCollection->id,
        'formatted' => 'Am 1/2',
        'type' => VoteTypeEnum::AMENDMENT(),
        'remarks' => '102030',
    ])->create();

    VotingList::factory([
        'id' => 1,
        'description' => 'A9-0123/2021 - Name of rapporteur - Am 1/2',
        'reference' => 'A9-0123/2021',
    ])->withStats(30, 20, 10)->create();

    $this->action->execute();
})->throws(CouldNotMatchVoteException::class, 'Result for matched voting list 1 and vote 1 are not equal');
