<?php

namespace App\Enums;

use Spatie\Enum\Laravel\Enum;

/**
 * @method static self FOR()
 * @method static self AGAINST()
 * @method static self ABSTENTION()
 * @method static self NOVOTE()
 */
class VotePositionEnum extends Enum
{
    protected static function values(): array
    {
        return [
            'FOR' => 0,
            'AGAINST' => 1,
            'ABSTENTION' => 2,
            'NOVOTE' => 3,
        ];
    }
}
