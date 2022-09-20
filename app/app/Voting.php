<?php

namespace App;

use App\Enums\VotePositionEnum;
use Illuminate\Database\Eloquent\Relations\Pivot;

class Voting extends Pivot /*
 * Votings connect VotingLists and Members. A Voting represents the vote
 * cast by one MEP during one vote. An MEP may be in favor of the motion,
 * against it, or abstain the vote.
 */
{
    protected $casts = [
        'position' => VotePositionEnum::class,
    ];
}
