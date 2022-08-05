<?php

namespace App\Enums;

use Spatie\Enum\Laravel\Enum;

/**
 * @method static self BRUSSELS()
 * @method static self STRASBOURG()
 * @method static self NONE()
 */
class LocationEnum extends Enum
{
    protected static function values(): array
    {
        return [
            'BRUSSELS' => 0,
            'STRASBOURG' => 1,
            'NONE' => 2,
        ];
    }

    protected static function labels(): array
    {
        return [
            'BRUSSELS' => 'Brussels',
            'STRASBOURG' => 'Strasbourg',
            'NONE' => 'None',
        ];
    }
}
