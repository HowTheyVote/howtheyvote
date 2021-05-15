<?php

namespace App\Exceptions;

use App\Vote;
use App\VotingList;
use Exception;

class CouldNotMatchVoteException extends Exception
{
    public static function noMatchingVotingList(Vote $vote): self
    {
        return new static("No voting list for vote {$vote->id} found.");
    }

    public static function multipleMatchingVotingLists(Vote $vote): self
    {
        return new static("Multiple voting lists for vote {$vote->id} found.");
    }

    public static function resultsDoNotMatch(Vote $vote, VotingList $votingList): self
    {
        return new static("Result for matched voting list {$votingList->id} and vote {$vote->id} are not equal.");
    }
}
