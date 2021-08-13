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
                report(CouldNotMatchVoteException::multipleMatchingVotingLists($vote));
                continue;
            }

            if ($count === 0) {
                report(CouldNotMatchVoteException::noMatchingVotingList($vote));
                continue;
            }

            $votingList = $votingLists->first();

            $stats = $votingList->stats['by_position'];
            $resultString = $stats['FOR'].$stats['AGAINST'].$stats['ABSTENTION'];

            if ($resultString !== $vote->remarks) {
                report(CouldNotMatchVoteException::resultsDoNotMatch($vote, $votingList));
                continue;
            }

            $votingList = $votingList->update([
                'vote_id' => $vote->id,
            ]);
        }
    }
}
