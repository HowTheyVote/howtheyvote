<?php

namespace App\Enums;

use Spatie\Enum\Laravel\Enum;

/**
 * @method static self BRUSSELS()
 * @method static self STRASBOURG()
 */
class LocationEnum extends Enum
{
    protected static function values(): array
    {
        return [
            'BRUSSELS' => 0,
            'STRASBOURG' => 1,
        ];
    }

    protected static function labels(): array
    {
        return [
            'BRUSSELS' => 'Brussels',
            'STRASBOURG' => 'Strasbourg',
        ];
    }
}
