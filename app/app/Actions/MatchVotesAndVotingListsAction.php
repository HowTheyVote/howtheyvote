<?php

namespace App\Actions;

use App\Exceptions\CouldNotMatchVoteException;
use App\Vote;
use App\VotingList;

class MatchVotesAndVotingListsAction extends Action
{
    public function execute(): void
    {
        $votesToMatch = Vote::whereDoesntHave('votingList')
            ->where('unmatched', false)
            ->get();

        $sharePicAction = new GenerateVoteSharePicAction();

        $totalUnmatched = $votesToMatch->count();

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

            $votingList->update([
                'vote_id' => $vote->id,
            ]);

            if ($vote->isFinalVote()) {
                $sharePicAction->execute($votingList);
            }
        }

        $remainingUnmatched = Vote::query()
            ->whereDoesntHave('votingList')
            ->where('unmatched', false)
            ->count();

        $recentlyMatched = $totalUnmatched - $remainingUnmatched;

        $this->log("Matched {$recentlyMatched} votes. {$remainingUnmatched} votes are still unmatched.");
    }
}
