<?php

namespace App\Enums;

use App\Casts\EnumCast;
use Illuminate\Contracts\Database\Eloquent\CastsAttributes;
use Spatie\Enum\Laravel\Enum as BaseEnum;

class Enum extends BaseEnum
{
    public static function castUsing(array $arguments): CastsAttributes
    {
        return new EnumCast(static::class, ...$arguments);
    }
}
