<?php

namespace App\Enums;

enum VoteTypeEnum: int
{
    case PRIMARY = 0;
    case AMENDMENT = 1;
    case SEPARATE = 2;

    public static function make(string $type): static
    {
        return match ($type) {
            'PRIMARY' => static::PRIMARY,
            'AMENDMENT' => static::AMENDMENT,
            'SEPARATE' => static::SEPARATE,
        };
    }
}
