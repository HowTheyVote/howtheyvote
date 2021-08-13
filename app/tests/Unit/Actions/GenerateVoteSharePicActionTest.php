<?php

use App\Actions\GenerateVoteSharePicAction;
use App\Vote;
use App\VotingList;
use Illuminate\Foundation\Testing\RefreshDatabase;

uses(Tests\TestCase::class, RefreshDatabase::class);

beforeEach(function () {
    Storage::fake('public');

    $this->action = new GenerateVoteSharePicAction();

    $this->votingList = VotingList::factory([
        'vote_id' => Vote::factory(),
    ])->withStats()->create();
});

it('uploads an image', function () {
    $this->action->execute($this->votingList);

    expect(Storage::disk('public')->exists("share-pictures/vote-sharepic-{$this->votingList->id}.png"))->toEqual(true);
});

it('does not create a new one if a share-pic already exists', function () {
    $this->action->execute($this->votingList);

    $modifiedTimestamp = Storage::disk('public')->lastModified("share-pictures/vote-sharepic-{$this->votingList->id}.png");

    $this->action->execute($this->votingList);

    expect(Storage::disk('public')->lastModified("share-pictures/vote-sharepic-{$this->votingList->id}.png"))->toEqual($modifiedTimestamp);
});
