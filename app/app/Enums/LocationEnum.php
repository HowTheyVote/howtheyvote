<?php

namespace App\Enums;

enum LocationEnum: int
{
    case BRUSSELS = 0;
    case STRASBOURG = 1;
    case NONE = 2;

    public function label(): string
    {
        return match ($this) {
            self::BRUSSELS => 'Brussels',
            self::STRASBOURG => 'Strasbourg',
            self::NONE => 'None',
        };
    }

    public static function make(string $location): static
    {
        return match ($location) {
            'BRUSSELS' => static::BRUSSELS,
            'STRASBOURG' => static::STRASBOURG,
            'NONE' => static::NONE,
        };
    }
}
