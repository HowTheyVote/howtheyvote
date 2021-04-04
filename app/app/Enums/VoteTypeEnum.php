<?php

namespace App\Enums;

use Spatie\Enum\Laravel\Enum;

/**
 * @method static self FINAL()
 * @method static self AMENDMENT()
 * @method static self SPLIT()
 * @method static self AGENDA()
 */
class VoteTypeEnum extends Enum
{
    protected static function values(): array
    {
        return [
            'FINAL' => 0,
            'AMENDMENT' => 1,
            'SPLIT' => 2,
            'AGENDA' => 3,
        ];
    }
}
