<?php

namespace App;

use App\Enums\VotePositionEnum;
use Illuminate\Database\Eloquent\Relations\Pivot;

class MemberVote extends Pivot
{
    protected $casts = [
        'position' => VotePositionEnum::class,
    ];
}
