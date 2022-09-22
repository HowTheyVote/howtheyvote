<?php

namespace App\Enums;

enum VotePositionEnum: int
{
    case FOR = 0;
    case AGAINST = 1;
    case ABSTENTION = 2;
    case NOVOTE = 3;

    public function label(): string
    {
        return match ($this) {
            self::FOR => 'FOR',
            self::AGAINST => 'AGAINST',
            self::ABSTENTION => 'ABSTENTION',
            self::NOVOTE => 'NOVOTE',
        };
    }

    public static function make(string|int $position): static
    {
        return match ($position) {
            'FOR' => static::FOR,
            'AGAINST' => static::AGAINST,
            'ABSTENTION' => static::ABSTENTION,
            'NOVOTE' => static::NOVOTE,
            0 => static::FOR,
            1 => static::AGAINST,
            2 => static::ABSTENTION,
            3 => static::NOVOTE,
        };
    }

    public static function toValues()
    {
        return array_map(
            fn (VotePositionEnum $c) => $c->name,
            VotePositionEnum::cases());
    }
}
