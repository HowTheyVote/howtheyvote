<?php

namespace App\Enums;

use Spatie\Enum\Laravel\Enum;

/**
 * @method static self PRIMARY()
 * @method static self AMENDMENT()
 * @method static self SEPARATE()
 */
class VoteTypeEnum extends Enum
{
    protected static function values(): array
    {
        return [
            'PRIMARY' => 0,
            'AMENDMENT' => 1,
            'SEPARATE' => 2,
        ];
    }
}
