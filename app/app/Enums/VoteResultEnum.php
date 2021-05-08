<?php

namespace App\Enums;

use Spatie\Enum\Laravel\Enum;

/**
 * @method static self ADOPTED()
 * @method static self REJECTED()
 */
class VoteResultEnum extends Enum
{
    protected static function values(): array
    {
        return [
            'ADOPTED' => 0,
            'REJECTED' => 1,
        ];
    }
}
