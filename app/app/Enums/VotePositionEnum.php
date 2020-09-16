<?php

namespace App\Enums;

use Spatie\Enum\Enum;

/**
 * @method static self FOR()
 * @method static self AGAINST()
 * @method static self ABSTENTION()
 */
class VotePositionEnum extends Enum
{
    protected static function values(): array
    {
        return [
            'FOR' => 0,
            'AGAINST' => 1,
            'ABSTENTION' => 2,
        ];
    }
}
