<?php

namespace App\Actions;

use App\Exceptions\CouldNotMatchVoteException;
use App\Vote;
use App\VotingList;

class MatchVotesAndVotingListsAction extends Action
{
    public function execute(): void
    {
        $votesToMatch = Vote::whereDoesntHave('votingList')->get();

        foreach ($votesToMatch as $vote) {
            $votingLists = null;

            if ($vote->reference) {
                $votingLists = VotingList::where('vote_id', null)
                    ->where('description', 'like', "%{$vote->reference}%{$vote->formatted}");
            }

            if (! $votingLists || $votingLists->count() === 0) {
                $votingLists = VotingList::where('vote_id', null)
                    ->where('description', 'like', "%{$vote->voteCollection->reference}%{$vote->formatted}");
            }

            $count = $votingLists->count();

            if ($count > 1) {
                throw CouldNotMatchVoteException::multipleMatchingVotingLists($vote);
            }

            if ($count === 0) {
                throw CouldNotMatchVoteException::noMatchingVotingList($vote);
            }

            $votingList = $votingLists->first();

            $stats = $votingList->stats['by_position'];
            $resultString = $stats['FOR'].$stats['AGAINST'].$stats['ABSTENTION'];

            if ($resultString !== $vote->remarks) {
                throw CouldNotMatchVoteException::resultsDoNotMatch($vote, $votingList);
            }

            $votingList = $votingList->update([
                'vote_id' => $vote->id,
            ]);
        }
    }
}
