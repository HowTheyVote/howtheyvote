<?php

namespace App\Exceptions;

use Exception;

class NoResponseException extends Exception
{
    public static function forVotingLists(string $date): self
    {
        return new static("Got null response. No VotingLists imported for {$date}.");
    }

    public static function forVoteCollections(string $date): self
    {
        return new static("Got null response. No VoteCollections imported for {$date}.");
    }

    public static function forMembers(): self
    {
        return new static('Got null response. No Members imported.');
    }

    public static function forMembersGroupmemberships(): self
    {
        return new static('Got null response. No GroupMemberships imported.');
    }
}
