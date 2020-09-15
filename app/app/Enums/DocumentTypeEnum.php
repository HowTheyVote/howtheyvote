<?php

namespace App\Enums;

use Spatie\Enum\Enum;

/**
 * @method static self A()
 * @method static self B()
 * @method static self RC()
 */
class DocumentTypeEnum extends Enum
{
    protected static function values(): array
    {
        return [
            'A' => 0,
            'B' => 1,
            'RC' => 2,
        ];
    }
}
