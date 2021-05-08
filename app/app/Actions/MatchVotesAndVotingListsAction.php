<?php

namespace App\Actions;

use App\Vote;
use App\VotingList;

class MatchVotesAndVotingListsAction extends Action
{
    public function execute(): void
    {
        $votesToMatch = Vote::whereDoesntHave('votingList')->get();

        foreach ($votesToMatch as $vote) {
            $votingLists = VotingList::where('vote_id', null)
                ->where('description', 'like', "%{$vote->voteCollection->reference} - %{$vote->formatted}");

            if ($votingLists->count() > 1) {
                throw new Exception("Multiple matching voting lists found for vote {$vote->id}.");
            }

            $votingList = $votingLists->first()->update([
                'vote_id' => $vote->id,
            ]);
        }
    }
}
